def createExceptionResponse(msg):
	return {"status":"exception",
				"response": msg}

def createSuccessResponse(msg):
	return {"status":"success",
				"response": msg}