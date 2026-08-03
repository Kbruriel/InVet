# QA-004 Results

## Validation summary

- Public branch profile endpoint returns public data.
- Protected branch profile endpoint requires authentication.
- The slice keeps the public and protected contracts separated.

## Commands executed

```text
C:\Users\Precision 7520\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest backend/app/tests -q
```

## Execution result

- `18 passed`
- The run completed successfully.
- Output included deprecation warnings from `sqlalchemy`, `pytest_asyncio`, `fastapi.testclient`, and `pydantic`, but no failing tests.

## Implemented endpoints

- `GET /api/v1/clinics/branches/{branch_id}` - public branch profile without authentication.
- `GET /api/v1/clinics/{clinic_id}/{branch_id}` - protected branch profile with authentication and access control.

## Notes

- No ORM models are exposed in the API response.
- Error handling stays consistent with the slice contract.
- The route shape now matches the BE-004 task spec and QA contract.
