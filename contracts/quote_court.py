# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""Source-bound provider selection and receipt-gated purchasing for AI agents."""

from genlayer import *
import hashlib
import json
import typing

SNAPSHOT_LIMIT = 3200


class QuoteCourt(gl.Contract):
    request_count: u64
    latest_request_id: str
    latest_decision_id: str
    latest_challenge_id: str
    latest_authorization_id: str
    latest_execution_id: str
    requests: TreeMap[str, str]
    decisions: TreeMap[str, str]
    challenges: TreeMap[str, str]
    authorizations: TreeMap[str, str]
    executions: TreeMap[str, str]
    request_ids: DynArray[str]

    def __init__(self):
        self.request_count = u64(0)
        self.latest_request_id = ""
        self.latest_decision_id = ""
        self.latest_challenge_id = ""
        self.latest_authorization_id = ""
        self.latest_execution_id = ""

    @gl.public.view
    def get_quote_request(self, request_id: str) -> str:
        return self.requests.get(request_id.strip(), "")

    @gl.public.view
    def get_quote_decision(self, decision_id: str) -> str:
        return self.decisions.get(decision_id.strip(), "")

    @gl.public.view
    def get_quote_challenge(self, challenge_id: str) -> str:
        return self.challenges.get(challenge_id.strip(), "")

    @gl.public.view
    def get_purchase_authorization(self, authorization_id: str) -> str:
        return self.authorizations.get(authorization_id.strip(), "")

    @gl.public.view
    def get_purchase_execution(self, execution_id: str) -> str:
        return self.executions.get(execution_id.strip(), "")

    @gl.public.view
    def list_quote_request_ids(self) -> str:
        return _canonical_json([request_id for request_id in self.request_ids])

    @gl.public.write
    def register_quote_request(self, purchase_intent: str, selection_policy: str, max_spend: str, provider_a_url: str, provider_b_url: str, challenge_window_seconds: str) -> str:
        intent = _clean(purchase_intent, 320, "purchase_intent_required")
        policy = _clean(selection_policy, 420, "selection_policy_required")
        cap = _money(max_spend)
        window = _window(challenge_window_seconds)
        sources = [_source("provider_a", provider_a_url), _source("provider_b", provider_b_url)]

        def leader_fn():
            return _canonical_json(_baseline(intent, policy, cap, _render_all(sources)))

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                return _canonical_json(json.loads(leader_result.value)) == _canonical_json(_baseline(intent, policy, cap, _render_all(sources)))
            except Exception:
                return False

        baseline = json.loads(gl.vm.run_nondet_unsafe(leader_fn, validator_fn))
        request_id = "qte_" + _sha256(intent + "|" + policy + "|" + baseline["baseline_hash"])[:20]
        if self.requests.get(request_id, ""):
            raise Exception("quote_request_already_registered")
        request = {"id": request_id, "purchase_intent": intent, "selection_policy": policy, "max_spend": cap, "provider_sources": baseline["snapshots"], "snapshot_commitments": baseline["snapshot_commitments"], "baseline_hash": baseline["baseline_hash"], "challenge_window_seconds": window, "status": "open", "decision_id": "", "challenge_id": "", "authorization_id": "", "created_at": _now()}
        self.requests[request_id] = _canonical_json(request)
        self.request_ids.append(request_id)
        self.request_count = u64(int(self.request_count) + 1)
        self.latest_request_id = request_id
        return request_id

    @gl.public.write
    def assess_provider_quotes(self, request_id: str) -> str:
        request = _load(self.requests, request_id, "unknown_quote_request")
        if request["status"] != "open":
            raise Exception("request_not_open_for_assessment")

        def leader_fn():
            return _canonical_json(_assessment(request))

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                return _same_assessment(json.loads(leader_result.value), _assessment(request))
            except Exception:
                return False

        result = json.loads(gl.vm.run_nondet_unsafe(leader_fn, validator_fn))
        decision_id = "qdc_" + _sha256(request["id"] + "|" + result["decision_hash"])[:20]
        if self.decisions.get(decision_id, ""):
            raise Exception("quote_decision_already_exists")
        decision = {"id": decision_id, "request_id": request["id"], "outcome": result["outcome"], "selected_provider_role": result["selected_provider_role"], "approved_spend": result["approved_spend"], "summary": result["summary"], "evidence_commitment": result["evidence_commitment"], "decision_hash": result["decision_hash"], "baseline_hash": request["baseline_hash"], "created_at": _now()}
        request["status"] = "reviewed"
        request["decision_id"] = decision_id
        request["challenge_deadline"] = _now() + int(request["challenge_window_seconds"])
        self.requests[request["id"]] = _canonical_json(request)
        self.decisions[decision_id] = _canonical_json(decision)
        self.latest_decision_id = decision_id
        return decision_id

    @gl.public.write
    def challenge_quote_decision(self, request_id: str, decision_id: str, counterevidence_url: str) -> str:
        request = _load(self.requests, request_id, "unknown_quote_request")
        if request["status"] != "reviewed" or request["decision_id"] != decision_id.strip():
            raise Exception("decision_not_challengeable")
        if _now() > int(request["challenge_deadline"]):
            raise Exception("challenge_window_closed")
        decision = _load(self.decisions, decision_id, "unknown_quote_decision")
        source = _source("counterevidence", counterevidence_url)

        def leader_fn():
            return _canonical_json(_render(source))

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                return _canonical_json(json.loads(leader_result.value)) == _canonical_json(_render(source))
            except Exception:
                return False

        snapshot = json.loads(gl.vm.run_nondet_unsafe(leader_fn, validator_fn))
        challenge_id = "qch_" + _sha256(request["id"] + "|" + decision["decision_hash"] + "|" + snapshot["snapshot_hash"])[:20]
        if self.challenges.get(challenge_id, ""):
            raise Exception("quote_challenge_already_exists")
        challenge = {"id": challenge_id, "request_id": request["id"], "decision_id": decision["id"], "counterevidence": snapshot, "baseline_hash": request["baseline_hash"], "status": "pending_resolution", "created_at": _now()}
        request["status"] = "challenged"
        request["challenge_id"] = challenge_id
        self.requests[request["id"]] = _canonical_json(request)
        self.challenges[challenge_id] = _canonical_json(challenge)
        self.latest_challenge_id = challenge_id
        return challenge_id

    @gl.public.write
    def resolve_quote_challenge(self, request_id: str, challenge_id: str) -> str:
        request = _load(self.requests, request_id, "unknown_quote_request")
        if request["status"] != "challenged" or request["challenge_id"] != challenge_id.strip():
            raise Exception("challenge_not_pending")
        decision = _load(self.decisions, request["decision_id"], "unknown_quote_decision")
        challenge = _load(self.challenges, challenge_id, "unknown_quote_challenge")
        result = _resolution(request, decision, challenge)
        challenge["status"] = "resolved"
        challenge["resolution"] = result
        request["status"] = "resolved"
        self.challenges[challenge_id] = _canonical_json(challenge)
        self.requests[request["id"]] = _canonical_json(request)
        return challenge_id

    @gl.public.write
    def finalize_purchase_authorization(self, request_id: str, authorization_window_seconds: str) -> str:
        request = _load(self.requests, request_id, "unknown_quote_request")
        if request["status"] == "reviewed" and _now() <= int(request["challenge_deadline"]):
            raise Exception("challenge_window_still_open")
        if request["status"] not in ["reviewed", "resolved"]:
            raise Exception("request_not_finalizable")
        decision = _load(self.decisions, request["decision_id"], "unknown_quote_decision")
        final = decision
        resolution_hash = ""
        if request["status"] == "resolved":
            challenge = _load(self.challenges, request["challenge_id"], "unknown_quote_challenge")
            final = challenge["resolution"]
            resolution_hash = final["resolution_hash"]
        if final["outcome"] != "approved":
            raise Exception("no_approved_purchase_authorization")
        provider = _provider_source(request, final["selected_provider_role"])
        authorization_id = "qau_" + _sha256(request["id"] + "|" + decision["decision_hash"] + "|" + resolution_hash + "|" + final["approved_spend"])[:20]
        if self.authorizations.get(authorization_id, ""):
            raise Exception("purchase_authorization_already_finalized")
        authorization = {"id": authorization_id, "request_id": request["id"], "decision_id": decision["id"], "provider_role": final["selected_provider_role"], "provider_url": provider["canonical_url"], "spend_cap": final["approved_spend"], "baseline_hash": request["baseline_hash"], "decision_hash": decision["decision_hash"], "resolution_hash": resolution_hash, "expires_at": _now() + _window(authorization_window_seconds), "status": "approved", "execution_id": ""}
        request["status"] = "authorized"
        request["authorization_id"] = authorization_id
        self.requests[request["id"]] = _canonical_json(request)
        self.authorizations[authorization_id] = _canonical_json(authorization)
        self.latest_authorization_id = authorization_id
        return authorization_id

    @gl.public.write
    def execute_authorized_purchase(self, request_id: str, authorization_id: str, provider_url: str, spend_amount: str) -> str:
        request = _load(self.requests, request_id, "unknown_quote_request")
        authorization = _load(self.authorizations, authorization_id, "unknown_purchase_authorization")
        spend = _money(spend_amount)
        if request["status"] != "authorized" or request["authorization_id"] != authorization["id"]:
            raise Exception("authorization_not_active")
        if authorization["status"] != "approved" or _now() > int(authorization["expires_at"]):
            raise Exception("authorization_expired_or_consumed")
        if provider_url.strip() != authorization["provider_url"]:
            raise Exception("provider_not_authorized")
        if _to_micros(spend) > _to_micros(authorization["spend_cap"]):
            raise Exception("spend_cap_exceeded")
        execution_id = "qex_" + _sha256(authorization["id"] + "|" + provider_url.strip() + "|" + spend)[:20]
        execution = {"id": execution_id, "request_id": request["id"], "authorization_id": authorization["id"], "provider_url": authorization["provider_url"], "spend_amount": spend, "spend_cap": authorization["spend_cap"], "executed_at": _now()}
        authorization["status"] = "consumed"
        authorization["execution_id"] = execution_id
        request["status"] = "executed"
        self.authorizations[authorization["id"]] = _canonical_json(authorization)
        self.requests[request["id"]] = _canonical_json(request)
        self.executions[execution_id] = _canonical_json(execution)
        self.latest_execution_id = execution_id
        return execution_id


def _baseline(intent: str, policy: str, cap: str, snapshots: typing.Sequence[dict]) -> dict:
    commitments = _commitments(snapshots)
    return {"snapshots": snapshots, "snapshot_commitments": commitments, "baseline_hash": _sha256(_canonical_json({"purchase_intent": intent, "selection_policy": policy, "max_spend": cap, "snapshot_commitments": commitments}))}


def _assessment(request: dict) -> dict:
    evidence = request["provider_sources"]
    prompt = """You are a GenLayer consensus procurement adjudicator. Use only the supplied provider quote snapshots and selection policy. Pick provider_a or provider_b only when its quoted offer clearly satisfies the purchase intent, policy, and maximum spend. Otherwise return inconclusive. Return JSON with outcome (approved,declined,inconclusive), selected_provider_role (provider_a,provider_b,none), approved_spend as a decimal no greater than max_spend, confidence 0-100, and summary."""
    try:
        raw = json.loads(gl.nondet.exec_prompt(prompt + "\nContext: " + _canonical_json({"intent": request["purchase_intent"], "policy": request["selection_policy"], "max_spend": request["max_spend"], "evidence": evidence})))
    except Exception:
        raw = {"outcome": "inconclusive", "selected_provider_role": "none", "approved_spend": "0", "confidence": 0, "summary": "No parseable consensus decision."}
    return _decision(request, raw, evidence, "assessment")


def _resolution(request: dict, decision: dict, challenge: dict) -> dict:
    evidence = list(request["provider_sources"]) + [challenge["counterevidence"]]
    prompt = """You are a GenLayer consensus procurement adjudicator resolving a challenged provider selection. Use only the supplied evidence. Return JSON with outcome (approved,declined,inconclusive), selected_provider_role (provider_a,provider_b,none), approved_spend no greater than max_spend, confidence 0-100, and summary."""
    try:
        raw = json.loads(gl.nondet.exec_prompt(prompt + "\nContext: " + _canonical_json({"intent": request["purchase_intent"], "policy": request["selection_policy"], "max_spend": request["max_spend"], "prior_decision": decision, "evidence": evidence})))
    except Exception:
        raw = {"outcome": "inconclusive", "selected_provider_role": "none", "approved_spend": "0", "confidence": 0, "summary": "No parseable consensus resolution."}
    result = _decision(request, raw, evidence, "resolution")
    result["resolution_hash"] = _sha256(_canonical_json({"request_id": request["id"], "decision_hash": decision["decision_hash"], "challenge_id": challenge["id"], "evidence_commitment": result["evidence_commitment"], "outcome": result["outcome"], "selected_provider_role": result["selected_provider_role"], "approved_spend": result["approved_spend"]}))
    return result


def _decision(request: dict, raw: dict, evidence: typing.Sequence[dict], stage: str) -> dict:
    role = str(raw.get("selected_provider_role", "none")).lower()
    outcome = str(raw.get("outcome", "inconclusive")).lower()
    spend = _safe_money(raw.get("approved_spend", "0"))
    if role not in ["provider_a", "provider_b"] or outcome != "approved" or _to_micros(spend) <= 0 or _to_micros(spend) > _to_micros(request["max_spend"]):
        outcome, role, spend = "inconclusive", "none", "0"
    commitment = _sha256(_canonical_json({"baseline_hash": request["baseline_hash"], "snapshot_commitments": _commitments(evidence)}))
    result = {"outcome": outcome, "selected_provider_role": role, "approved_spend": spend, "confidence": _u8(raw.get("confidence", 0)), "summary": _clean(str(raw.get("summary", "No structured explanation returned.")), 320, "summary_required"), "evidence_commitment": commitment}
    result["decision_hash"] = _sha256(_canonical_json({"request_id": request["id"], "stage": stage, "baseline_hash": request["baseline_hash"], "evidence_commitment": commitment, "outcome": outcome, "selected_provider_role": role, "approved_spend": spend}))
    return result


def _same_assessment(left: dict, right: dict) -> bool:
    return all(left.get(key) == right.get(key) for key in ["outcome", "selected_provider_role", "approved_spend", "evidence_commitment", "decision_hash"])


def _provider_source(request: dict, role: str) -> dict:
    for source in request["provider_sources"]:
        if source["role"] == role:
            return source
    raise Exception("authorized_provider_missing")


def _render_all(sources: typing.Sequence[dict]) -> typing.Sequence[dict]:
    return [_render(source) for source in sources]


def _render(source: dict) -> dict:
    try:
        content, error = _bounded(gl.nondet.web.render(source["canonical_url"], mode="text"), SNAPSHOT_LIMIT), ""
    except Exception as exc:
        content, error = "", _bounded(str(exc), 240)
    return {"role": source["role"], "canonical_url": source["canonical_url"], "content": content, "snapshot_hash": _sha256(content) if content else "", "fetch_error_hash": _sha256(error) if error else ""}


def _commitments(snapshots: typing.Sequence[dict]) -> typing.Sequence[dict]:
    return [{"role": item["role"], "canonical_url": item["canonical_url"], "snapshot_hash": item["snapshot_hash"], "fetch_error_hash": item["fetch_error_hash"]} for item in snapshots]


def _load(records, record_id: str, error: str) -> dict:
    raw = records.get(record_id.strip(), "")
    if not raw:
        raise Exception(error)
    return json.loads(raw)


def _source(role: str, url: str) -> dict:
    clean = str(url).strip()
    if not clean.startswith("https://") or len(clean) > 280:
        raise Exception(role + "_url_required")
    return {"role": role, "canonical_url": clean}


def _clean(value: str, limit: int, error: str) -> str:
    clean = " ".join(str(value).strip().split())
    if not clean or len(clean) > limit:
        raise Exception(error)
    return clean


def _window(value: str) -> int:
    amount = int(str(value).strip())
    if amount < 60 or amount > 604800:
        raise Exception("invalid_window")
    return amount


def _money(value: str) -> str:
    clean = str(value).strip()
    if not clean or any(char not in "0123456789." for char in clean) or clean.count(".") > 1:
        raise Exception("invalid_spend_amount")
    return _safe_money(clean)


def _safe_money(value) -> str:
    try:
        whole, _, fraction = str(value).strip().partition(".")
        whole = str(int(whole or "0"))
        fraction = (fraction + "000000")[:6].rstrip("0")
        return whole + ("." + fraction if fraction else "")
    except Exception:
        return "0"


def _to_micros(value: str) -> int:
    whole, _, fraction = value.partition(".")
    return int(whole) * 1000000 + int((fraction + "000000")[:6])


def _u8(value) -> int:
    try:
        return max(0, min(100, int(value)))
    except Exception:
        return 0


def _bounded(value: str, limit: int) -> str:
    return " ".join(str(value).split())[:limit]


def _canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now() -> int:
    try:
        return int(gl.block.timestamp)
    except Exception:
        return 0
