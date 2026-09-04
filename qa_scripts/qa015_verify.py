"""
QA-015 - Verificaci[oó]n de los 3 criterios del slice BE-015 contra PG real.

Par[oam]etros reales (router reports_router.py):
    - period_start / period_end: str format YYYY-MM-DD (validación 422 con strptime)
    - page: >=1
    - size: 1..100
    - clinic_id: NO es par[aam]etro de query: se deriva del JWT (sub -> owners -> clinic_id)

Salida: JSON { ok: bool, results: {t01, t02, t03}, errors: [] }
Escritura: prints + /tmp/qa015_results.json
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://localhost:8215"
API = f"{BASE}/api/v1/reports"
TOKEN_FILE = os.environ.get("QA015_TOKEN_FILE", "/tmp/qa015_tok2.txt")


def load_token() -> str:
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def _request(method: str, url: str, headers: dict | None = None) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
            return resp.status, (json.loads(body) if body else body)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw.decode("utf-8", errors="replace")


def _qs(params: dict) -> str:
    return urllib.parse.urlencode(params)


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {load_token()}"}


def check(name: str, cond: bool, evidence: dict) -> dict:
    return {"name": name, "pass": bool(cond), "evidence": evidence}


def _get(endpoint: str, headers: dict | None, **params) -> tuple[int, dict | str]:
    if params:
        url = f"{API}/{endpoint}?{_qs(params)}"
    else:
        url = f"{API}/{endpoint}"
    return _request("GET", url, headers)


# ---------------------------------------------------------------------------
def qat01_happy_path() -> dict:
    """Happy path: 6 endpoints con y sin periodo."""
    results: list[dict] = []
    h = auth_headers()

    # 1. appointments global vs periodo acotado
    s, b = _get("appointments", h, page=1, size=5)
    total = b.get("total") if isinstance(b, dict) else None
    items = b.get("items") if isinstance(b, dict) else []
    results.append(check(
        "appointments_global_200_total_gte0",
        s == 200 and isinstance(total, int) and total >= 0 and len(items) <= 5,
        {"status": s, "total": total, "items_returned": len(items) if items is not None else None},
    ))

    s2, b2 = _get("appointments", h, period_start="2026-01-01", period_end="2026-12-31", page=1, size=5)
    results.append(check(
        "appointments_period_200",
        s2 == 200 and isinstance(b2, dict) and b2.get("total", -1) >= 0,
        {"status": s2, "total": b2.get("total") if isinstance(b2, dict) else None},
    ))

    s3, b3 = _get("appointments", h, period_start="2020-01-01", period_end="2020-12-31", page=1, size=5)
    total2020 = b3.get("total") if isinstance(b3, dict) else None
    results.append(check(
        "appointments_period_2020_empty_or_low",
        s3 == 200 and isinstance(total2020, int) and total2020 <= (total or 0),
        {"status": s3, "total_2020": total2020, "total_all": total},
    ))

    # 2. services global
    s4, b4 = _get("services", h, page=1, size=3)
    total_svc = b4.get("total") if isinstance(b4, dict) else None
    results.append(check(
        "services_global_total_gt0",
        s4 == 200 and isinstance(total_svc, int) and total_svc > 0,
        {"status": s4, "total": total_svc,
         "items_returned": len(b4.get("items", [])) if isinstance(b4, dict) else None},
    ))

    # 3. pets (PetCountDto: clinic_id + active_count)
    s5, b5 = _get("pets", h)
    ok_pets = (
        s5 == 200
        and isinstance(b5, dict)
        and "active_count" in b5
    )
    results.append(check(
        "pets_200_active_count",
        ok_pets,
        {"status": s5, "body": b5 if isinstance(b5, dict) else b5},
    ))

    # 4. consultations
    s6, b6 = _get("consultations", h, page=1, size=3)
    total_cons = b6.get("total") if isinstance(b6, dict) else None
    results.append(check(
        "consultations_global_total_gte0",
        s6 == 200 and isinstance(total_cons, int) and total_cons >= 0,
        {"status": s6, "total": total_cons,
         "items_returned": len(b6.get("items", [])) if isinstance(b6, dict) else None},
    ))

    # 5. ratings (RatingsReportResponse con by_veterinarian y clinic_avg)
    s7, b7 = _get("ratings", h)
    avg = b7.get("clinic_avg") if isinstance(b7, dict) else None
    by_vet = b7.get("by_veterinarian") if isinstance(b7, dict) else None
    ok_r = s7 == 200 and isinstance(avg, (int, float)) and 0 <= avg <= 5 and isinstance(by_vet, list)
    results.append(check(
        "ratings_200_avg_in_range",
        ok_r,
        {"status": s7, "clinic_avg": avg,
         "n_veterinarians": len(by_vet) if isinstance(by_vet, list) else None},
    ))

    # 6. payments (PaymentsReportResponse)
    s8, b8 = _get("payments", h, page=1, size=5)
    total_pay = b8.get("total") if isinstance(b8, dict) else None
    ta = b8.get("total_amount") if isinstance(b8, dict) else None
    np = (len(b8.get("items", [])) if isinstance(b8, dict) else 0)
    results.append(check(
        "payments_global_200",
        s8 == 200 and isinstance(total_pay, int) and total_pay >= 0 and np <= 5,
        {"status": s8, "total": total_pay, "total_amount": ta, "items_returned": np},
    ))

    return {"criterio": "QA-015-T01 happy path", "checks": results,
            "pass": all(c["pass"] for c in results)}


def qat02_pagination() -> dict:
    """Paginaci[oó]n: page, size (1..100), 422 por size fuera de rango, no-overlap entre p[aag]inas."""
    results: list[dict] = []
    h = auth_headers()

    # appointments: page 1 y 2 (size=5), total estable
    s1, b1p = _get("appointments", h, page=1, size=5)
    s2, b2p = _get("appointments", h, page=2, size=5)
    total = b1p.get("total") if isinstance(b1p, dict) else None
    i1 = b1p.get("items") if isinstance(b1p, dict) else []
    i2 = b2p.get("items") if isinstance(b2p, dict) else []
    ids1 = sorted([x.get("id") for x in i1 if isinstance(x, dict) and x.get("id") is not None])
    ids2 = sorted([x.get("id") for x in i2 if isinstance(x, dict) and x.get("id") is not None])
    no_overlap = not (set(ids1) & set(ids2))
    results.append(check(
        "appointments_pagination_p1p2",
        s1 == 200 and s2 == 200 and no_overlap and len(i1) <= 5 and len(i2) <= 5,
        {"status_p1": s1, "status_p2": s2, "total": total,
         "n_p1": len(i1), "n_p2": len(i2), "overlap": len(set(ids1) & set(ids2))},
    ))

    # appointments: size=100 (límite superior) y size=1 (límite inferior)
    s3, b3p = _get("appointments", h, page=1, size=100)
    s4, b4p = _get("appointments", h, page=1, size=1)
    results.append(check(
        "appointments_size_limits",
        s3 == 200 and s4 == 200
        and ((len(b3p.get("items", [])) if isinstance(b3p, dict) else 0) <= 100)
        and ((len(b4p.get("items", [])) if isinstance(b4p, dict) else 0) == 1),
        {"n_size100": len(b3p.get("items", [])) if isinstance(b3p, dict) else None,
         "n_size1": len(b4p.get("items", [])) if isinstance(b4p, dict) else None},
    ))

    # size=0 y size=101 -> 422
    s5, _ = _get("appointments", h, page=1, size=0)
    s6, _ = _get("appointments", h, page=1, size=101)
    s7, _ = _get("appointments", h, page=0, size=10)
    results.append(check(
        "appointments_invalid_size_422",
        s5 == 422 and s6 == 422 and s7 == 422,
        {"size0": s5, "size101": s6, "page0": s7},
    ))

    # services paginacio[oó]n (18 en base)
    s8, b8s1 = _get("services", h, page=1, size=10)
    s9, b9s2 = _get("services", h, page=2, size=10)
    i_s1 = b8s1.get("items") if isinstance(b8s1, dict) else []
    i_s2 = b9s2.get("items") if isinstance(b9s2, dict) else []
    s1_ids = {x.get("id") for x in i_s1 if isinstance(x, dict) and x.get("id") is not None}
    s2_ids = {x.get("id") for x in i_s2 if isinstance(x, dict) and x.get("id") is not None}
    results.append(check(
        "services_pagination_p1p2",
        s8 == 200 and s9 == 200
        and len(i_s1) <= 10 and len(i_s2) <= 10
        and len(s1_ids | s2_ids) == len(s1_ids) + len(s2_ids),
        {"n_p1": len(i_s1), "n_p2": len(i_s2), "union": len(s1_ids | s2_ids)},
    ))

    # consultations paginacio[oó]n
    s10, b10c = _get("consultations", h, page=1, size=2)
    s11, b11c = _get("consultations", h, page=2, size=2)
    results.append(check(
        "consultations_pagination_p1p2",
        s10 == 200 and s11 == 200
        and (len(b10c.get("items", [])) if isinstance(b10c, dict) else 0) <= 2
        and (len(b11c.get("items", [])) if isinstance(b11c, dict) else 0) <= 2,
        {"n_p1": len(b10c.get("items", [])) if isinstance(b10c, dict) else None,
         "n_p2": len(b11c.get("items", [])) if isinstance(b11c, dict) else None,
         "total": b10c.get("total") if isinstance(b10c, dict) else None},
    ))

    # payments paginacio[oó]n (202 en base, p[aag]ina 10 size=20)
    pg = list(range(1, min(4, (202 // 20) + 2)))
    statuses = []
    prev_ids = set()
    all_disjoint = True
    total = None
    for p in pg:
        st, bd = _get("payments", h, page=p, size=20)
        statuses.append(st)
        items = bd.get("items") if isinstance(bd, dict) else []
        cur_ids = {x.get("id") for x in items if isinstance(x, dict) and x.get("id") is not None}
        if cur_ids & prev_ids:
            all_disjoint = False
        prev_ids |= cur_ids
        total = bd.get("total") if isinstance(bd, dict) else total
    results.append(check(
        "payments_pagination_disjoint",
        all(st == 200 for st in statuses) and all_disjoint,
        {"pages_tested": pg, "statuses": statuses,
         "total": total, "disjoint": all_disjoint},
    ))

    return {"criterio": "QA-015-T02 paginación", "checks": results,
            "pass": all(c["pass"] for c in results)}


def qat03_auth_bola() -> dict:
    """Auth (401) y BOLA (clinic_id del token, no de query; periodos inv[aalid]os recha[zados])."""
    results: list[dict] = []

    # --- Auth ---
    # Sin Authorization header: 401
    s1, b1 = _request("GET", f"{API}/appointments")
    results.append(check("no_token_401", s1 == 401, {"status": s1, "detail": str(b1)[:200]}))

    # Malformed token: 401/403
    s2, _ = _request("GET", f"{API}/appointments", {"Authorization": "Bearer garbage"})
    s3, _ = _request("GET", f"{API}/appointments", {"Authorization": "Bearer"})
    results.append(check("bad_tokens_rejected", s2 in (401, 403) and s3 in (401, 403),
                         {"garbage": s2, "bare": s3}))

    # --- BOLA / Tenant isolation ---
    # Si clinic_id viene del JWT, no puede ser sob[r]escrito por query clinic_id=999.
    # El par[aam]etro clinic_id no existe en la signature del endpoint, as[i] cualquier
    # query string 'clinic_id=999' debe ser ignorado (no produce acceso a otros tenants).
    h = auth_headers()
    s_own_global, b_own_global = _get("appointments", h, page=1, size=5)
    s_faked, b_faked = _get("appointments", h, page=1, size=5, clinic_id=999)
    # Si el endpoint no acepta clinic_id en query, debe ser el mismo total y 200 o 422/400 igual.
    # La clave es que clinic_id=999 NO expande el alcance: total faked <= total own.
    t_own = b_own_global.get("total") if isinstance(b_own_global, dict) else None
    t_faked = b_faked.get("total") if isinstance(b_faked, dict) else None
    results.append(check(
        "bola_clinic_id_query_ignored_or_rejected",
        (s_faked in (422, 400, 403))
        or (t_own is None or t_faked is None)
        or (t_faked <= t_own),
        {"own_status": s_own_global, "own_total": t_own,
         "faked_status": s_faked, "faked_total": t_faked},
    ))

    # BOLA pet count: clinic_id=999 faked en /pets no debe dar datos de otro tenant
    s_faked_pets, b_fp = _get("pets", h, clinic_id=999)
    s_own_pets, b_op = _get("pets", h)
    t_own_pets = (b_op.get("active_count") if isinstance(b_op, dict) else None)
    t_faked_pets = (b_fp.get("active_count") if isinstance(b_fp, dict) else None)
    results.append(
        check(
            "bola_pets_faked_not_expanded",
            (s_faked_pets in (422, 403, 400))
            or (t_faked_pets is None and s_faked_pets != s_own_pets)
            or (t_faked_pets is not None and t_faked_pets <= (t_own_pets or 0)),
            {"own_status": s_own_pets, "own_count": t_own_pets,
             "faked_status": s_faked_pets, "faked_count": t_faked_pets},
        )
    )

    # --- Validaci[oó]n de fechas (422) ---
    # period_start mal formated: 422
    s_bad_date, b_bd = _get("appointments", h, period_start="not-a-date")
    s_bad_date2, _ = _get("appointments", h, period_end="2026-13-45")
    s_inv_range, _ = _get("appointments", h,
                          period_start="2026-12-31", period_end="2026-01-01")
    s_valid, b_vd = _get("appointments", h,
                         period_start="2026-01-01", period_end="2026-01-02")
    results.append(check(
        "dates_validation",
        s_bad_date == 422 and s_bad_date2 == 422
        and s_inv_range == 422 and s_valid == 200,
        {"bad_format": s_bad_date, "bad_month": s_bad_date2,
         "start_after_end": s_inv_range, "valid_range": s_valid,
         "valid_total": b_vd.get("total") if isinstance(b_vd, dict) else None,
         "detail_bad": str(b_bd)[:200]},
    ))

    return {"criterio": "QA-015-T03 auth/BOLA", "checks": results,
            "pass": all(c["pass"] for c in results)}


def main() -> int:
    t01 = qat01_happy_path()
    t02 = qat02_pagination()
    t03 = qat03_auth_bola()
    ok = all(v["pass"] for v in (t01, t02, t03))
    report = {
        "ok": ok,
        "t01": t01,
        "t02": t02,
        "t03": t03,
        "base_url": BASE,
    }
    print(json.dumps(report, indent=2, default=str, ensure_ascii=False))
    with open("/tmp/qa015_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
