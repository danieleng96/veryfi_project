cols = ['Assembly_Step',	'IQC',	'LD',	'APD','TestQC',	'Mirror',	'MirrorQC',	'Lens',	'LensQC',	'Final',	'FinalQC',	'Placement',	'LecQC']
tray = 'XXXXX-02S'
query_start = 'Select '
for col in cols:
    query_start = query_start+ f'SUM(CASE WHEN {col} = 1 THEN 1 else 0 END) {col}_Fails, '
for col in cols:
    query_start = query_start + f'count(*) - count({col}) {col},'


query_start = query_start + f'count(*) total from labview.dbo.ProductionTracker where TrayName = \'{tray}\''
print(query_start)

