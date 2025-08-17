from fastapi import HTTPException


def bad_request(detail: str) -> HTTPException:
	return HTTPException(status_code=400, detail=detail)


def not_found(detail: str = "Not found") -> HTTPException:
	return HTTPException(status_code=404, detail=detail)


def unprocessable(detail: str) -> HTTPException:
	return HTTPException(status_code=422, detail=detail)
