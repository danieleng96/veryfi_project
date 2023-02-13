location = ({'user': '', 'pwd': '', 'server': 'vl-mes-db01.velodyne.com',
                  "db": 'labview', 'trusted': 'yes'},
                 {'user': 'VL_STARS', 'pwd': r'irtfs5#935', 'server': 'vl-mes.database.windows.net', "db": 'labview2',
                  'trusted': 'no'},{'user': 'VL_Fabrinet', 'pwd': r'iku7kRD#234', 'server': 'vl-mes.database.windows.net', 'db':'labview','trusted': 'no'})
#0 = San Jose, 1 = STARS, 2 = Fabrinet

inverted_list = ['Face UP', 'Face DOWN']

dimensions_dict = {"APA": [5, 7], "TROSA_101": [6, 5], "VLX": [5,5]}

rows_dict = {"APA": 4, "TROSA_101": 8, "VLX": 4}

colordic = {"AllPassed": "green", "Passed": "lightgreen", "Failed": "#FFBDBB", "Velobit": "yellow", None: "gray",
            "Untested": "lightgray", "Failing_Chs:": "#BBB0FF"}

today = ['', ' and convert(varchar(10), TStamp, 102) = convert(varchar(10), getdate(), 102)']
velobit_ch_rnd = 5
test_order = ['LD','BB','APD','Final']
breakdown_color = ['lightgreen', 'pink', 'lightblue','#fff266']
prod_ch = {'APA':4, "TROSA_101":8, "VLX":4}
asic_lp_settings = {'LP14_Output':['14','5','2.5'],'LP12_Output':['12','5','2.5'],'LP0_Output':['0','5','2.5'], 'LP0_High':['0','8','3']}
asic_lp_list = [['14','5','2.5'],['12','5','2.5'],['0','5','2.5'],['0','8','3']]

set_pl = ''

#excelitas APD data_sheet
volts_degree_c = -1.3
vpd_error = 0.2
#V/C