from plots import *


def regress(group,cta):
	con = sqlite3.connect('data/edp_changes.db')
	cur = con.cursor()
	q = create_query(group,cta)
	cur.execute(q)

	con = sqlite3.connect('data/edp_changes.db')
	cur = con.cursor()
	q = create_query(group,cta)
	X =[]
	y= []
	cur.execute(q)
	
	for row in cur:
		X.append (np.array([ safe_float(row[0]), safe_float(row[1]) ] )) 
		y.append ( safe_float(row[2]) )

	y = np.array(y)
	X = np.array(X)
	X = sm.add_constant(X)
	model_result = sm.OLS(y,X).fit()
	return model_result
	

def write_result(model_result,group,cta):
	fname = 'results/%s/reg/%s.txt'%(create_fname(cta), group)
	result_doc = open(fname,'w+')
	result_doc.write( model_result.summary().as_text() )
	result_doc.close()


def make_reg_folders(cta):
	"""set up the required folder structure"""
	make_all_folders(cta)
	make_folder('results/%s/reg/'%(create_fname(cta)))


def run_regs(cta):
	"""combines all the functions to make all the plots"""
	con = sqlite3.connect('data/edp_changes.db')
	cur = con.cursor()
	cur.execute(( "select * from group_edps "+
		" where group_edps.dim_cta_key = %s group by dim_group_key"%cta) )

	groups = cur.fetchall()
	for group in groups:
		if  (('64' not in  str(group[0]))
		and ('48' not in  str(group[0]))) :
			model_result = regress(str(group[0]),cta)
			write_result(model_result,group,cta)


def plot_coefficients(cta):

	fig = plt.figure()
	
	con = sqlite3.connect('data/edp_changes.db')
	cur = con.cursor()
	cur.execute(( "select * from group_edps "+
		" where group_edps.dim_cta_key = %s group by dim_group_key"%cta) )

	groups = cur.fetchall()
	
	vols =[]
	lb = [[],[],[]]
	ub = [[],[],[]]
	mean = [[],[],[]]

	for group in groups:
		group = str(group[0])
		if  (('64' not in  group)
		and  ('48' not in  group)) :
			model_result = regress(group,cta)
			conf_int = model_result.conf_int()

			query = ("select avg(group_edps.eq_vol) from group_edps "+
			" where group_edps.dim_cta_key = %s and group_edps.dim_group_key = '%s' "%(cta,group) +
			" group by dim_group_key")
			cur.execute(query )
			vol = cur.fetchall()
			
			vol = float(vol[0][0])

			vols.append(vol)
			for coef in range(3):
				lb[coef].append(conf_int[coef][0])
				ub[coef].append(conf_int[coef][1])
				mean[coef].append( (lb[coef][-1] + ub[coef][-1])/2.0 )


	for coef in range(3):
		plt.plot(vols, mean[coef], 'ro', vols, lb[coef], 'b^', vols, ub[coef], 'g^')
		plt.savefig('results/%s/coef_%s.png'%(create_fname(cta), coef))
		plt.close()



def run_all_regs():
	for cta in CTAS:
		make_reg_folders(cta)
		run_regs(cta)


def make_all_reg_plots():
	for cta in CTAS:
		make_reg_folders(cta)
		plot_coefficients(cta)



if __name__ == "__main__":
	 make_all_reg_plots()