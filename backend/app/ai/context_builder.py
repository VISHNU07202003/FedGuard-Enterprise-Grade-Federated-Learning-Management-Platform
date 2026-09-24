import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import TrainingRun, GlobalMetric, PrivacyConfigModel, TrainingRound
from app.schemas.copilot import CopilotContext, CopilotSource

async def build_context(db: AsyncSession, ctx: CopilotContext) -> tuple[str, list[CopilotSource]]:
    context_data = {
        "observability": "Observability is enabled via Prometheus and Grafana (Phase 13B). Metrics are exposed at /metrics on backend."
    }
    sources = []

    if ctx.run_id:
        # Fetch Run Metadata
        run_result = await db.execute(select(TrainingRun).where(TrainingRun.run_id == ctx.run_id))
        run = run_result.scalars().first()
        if run:
            sources.append(CopilotSource(type="training_run", id=run.run_id))
            context_data["run"] = {
                "run_id": run.run_id,
                "model_type": run.model_type,
                "strategy": run.strategy,
                "status": run.status,
                "num_clients": run.num_clients,
                "num_rounds": run.num_rounds
            }
            
            # Fetch Metrics
            metric_result = await db.execute(select(GlobalMetric).where(GlobalMetric.run_id == ctx.run_id))
            metric = metric_result.scalars().first()
            if metric:
                sources.append(CopilotSource(type="global_metrics", id=run.run_id))
                context_data["final_metrics"] = {
                    "accuracy": metric.accuracy,
                    "loss": metric.loss,
                    "f1": metric.f1,
                    "roc_auc": metric.roc_auc,
                    "pr_auc": metric.pr_auc
                }

            # Fetch Privacy Config
            privacy_result = await db.execute(select(PrivacyConfigModel).where(PrivacyConfigModel.run_id == ctx.run_id))
            privacy = privacy_result.scalars().first()
            if privacy:
                sources.append(CopilotSource(type="privacy_config", id=run.run_id))
                context_data["privacy"] = {
                    "dp_enabled": privacy.dp_enabled,
                    "epsilon_spent": privacy.epsilon_spent,
                    "target_epsilon": privacy.target_epsilon,
                    "delta": privacy.delta
                }

            # Fetch rounds if asked
            if ctx.round_number is not None:
                round_result = await db.execute(
                    select(TrainingRound).where(TrainingRound.run_id == ctx.run_id, TrainingRound.round_number == ctx.round_number)
                )
                rnd = round_result.scalars().first()
                if rnd:
                    sources.append(CopilotSource(type="training_round", id=f"{run.run_id}:round-{rnd.round_number}"))
                    context_data["round_details"] = {
                        "round_number": rnd.round_number,
                        "status": rnd.status,
                        "accuracy": rnd.accuracy,
                        "loss": rnd.loss,
                        "clients_participated": rnd.clients_participated,
                        "straggler_count": rnd.straggler_count,
                        "clients_failed": rnd.clients_failed,
                        "clients_timed_out": rnd.clients_timed_out
                    }
                    
                    # Fetch edge metrics for this round
                    from app.db.models import RoundClient
                    edge_clients_result = await db.execute(
                        select(RoundClient).where(RoundClient.run_id == ctx.run_id, RoundClient.round_number == ctx.round_number)
                    )
                    edge_clients = edge_clients_result.scalars().all()
                    
                    if edge_clients:
                        # Only include edge context if edge data is actually present (e.g. non-null network latency)
                        has_edge_data = any(rc.network_latency_ms is not None for rc in edge_clients)
                        if has_edge_data:
                            sources.append(CopilotSource(type="edge_simulation", id=f"{run.run_id}:edge-round-{rnd.round_number}"))
                            
                            battery_skipped = sum(1 for rc in edge_clients if rc.availability_reason == "battery_low")
                            unavailable = sum(1 for rc in edge_clients if rc.availability_reason == "unavailable")
                            
                            valid_latencies = [rc.network_latency_ms for rc in edge_clients if rc.network_latency_ms is not None]
                            avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else None
                            
                            context_data["edge_simulation"] = {
                                "round_average_latency_ms": round(avg_latency, 2) if avg_latency else None,
                                "battery_skipped_clients": battery_skipped,
                                "probabilistic_unavailable_clients": unavailable,
                                "total_unavailable_edge_clients": battery_skipped + unavailable
                            }

    context_str = json.dumps(context_data, indent=2) if context_data else "No relevant context found."
    return context_str, sources
