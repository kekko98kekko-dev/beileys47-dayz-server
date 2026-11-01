from v36_nitrado_backups_readonly import analyze
def main():
 a=analyze({"backups":[]},{"restore_possible":True})
 assert a["backup_count"]==0 and not a["provider_backup_exists"] and not a["full_dayz_world_restore_tested"]
 b=analyze({"backups":[{"id":"sensitive-id","name":"private"}]},{"restore_possible":False})
 assert b["provider_backup_exists"] and b["backup_count"]==1 and b["restore_possible"] is False
 assert "sensitive-id" not in str(b) and "private" not in str(b)
 c=analyze({},None)
 assert c["backup_count"] is None and not c["provider_backup_exists"]
 assert not c["restore_reliability_certified"]
 print("PASS V36: distinguishes provider backup presence, restore option and untested recovery without leaking identifiers")
if __name__=="__main__":main()
