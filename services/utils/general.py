def RespApp(
        status=str,
        message=str,
        data=None,
) -> dict[str, any]:
    dt = {
        "status": status,
        "message": message,
        "data": data
    }
    return dt