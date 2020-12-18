import src.metadata


def driveTree(root, drive):
    def iterDrive(root, drive):
        params = {"pageToken": None, "supportsAllDrives": True, "includeItemsFromAllDrives": True,
                  "fields": "files(id,name,mimeType), incompleteSearch, nextPageToken", "q": "'"+root["id"]+"' in parents", "orderBy": "name"}
        while True:
            response = drive.files().list(**params).execute()
            for file in response["files"]:
                yield file
            try:
                params["pageToken"] = response["nextPageToken"]
            except KeyError:
                return
    if root["mimeType"] == "application/vnd.google-apps.folder":
        tree = root
        tree["type"] = "directory"
        tree["children"] = [driveTree(item, drive)
                            for item in iterDrive(root, drive)]
    elif "video" in root["mimeType"]:
        tree = root
        tree["type"] = "file"
    else:
        return

    return tree
