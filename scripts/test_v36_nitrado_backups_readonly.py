from v36_nitrado_backups_readonly import analyze
def main():
 a=analyze({"backups":[]},{"restore_possible":True})
 assert a["backup_count"]==0 and not a["provider_backup_exists"] and not a["full_dayz_world_restore_tested"]
 b=analyze({"backups":[{"id":"private","created":"2026-11-01"}]},{"restore_possible":False})
 assert b["provider_backup_exists"] and b["backup_count"]==1 and b["restore_possible"] is False
 assert "private" not in str(b)
 c=analyze({},None)
 assert c["backup_count"] is None and not c["provider_backup_exists"]
 assert not c["restore_reliability_certified"]
 d=analyze({"backups":{"full":[],"incremental":[]}},{"restore_possible":True})
 assert d["backup_count"]==0 and not d["provider_backup_exists"]
 e=analyze({"backups":{"full":[{"id":"secret-one","created":"2026-11-01"}],"incremental":[{"id":"secret-two","created":"2026-11-01"}]}},{"restore_possible":True})
 assert e["backup_count"]==2 and e["provider_backup_exists"] and "secret-two" not in str(e)
 f=analyze({"backups":{"meta":{"state":"active"},"categories":{"old":[],"new":[]}}},{"restore_possible":True})
 assert f["backup_count"]==0 and not f["provider_backup_exists"]
 print("PASS V36: correctly distinguishes actual nested backup records from category dictionary keys")
if __name__=="__main__":main()
