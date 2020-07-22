def pluginversion():
	try:
		with open("backendMetadata.json") as f:
			content = f.readlines()
			try:
				pluginversion = json.loads(content)["pluginversion"]
				return pluginversion
			except Exception as Ee:
				return {"status":"exception",
					"response": str(Ee)}
	except Exception as E:
		return {"status":"exception",
					"response": str(E)}