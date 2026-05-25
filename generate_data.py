import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random, warnings
warnings.filterwarnings('ignore')

def generate_loan_data(n=40000, seed=42):
    np.random.seed(seed); random.seed(seed)
    today = date(2026, 5, 25)

    # Reference Data 
    states_regions = {
        'Lagos':['South West'],'Ogun':['South West'],'Oyo':['South West'],
        'Osun':['South West'],'Ondo':['South West'],'Ekiti':['South West'],
        'Rivers':['South South'],'Delta':['South South'],'Edo':['South South'],
        'Bayelsa':['South South'],'Akwa Ibom':['South South'],'Cross River':['South South'],
        'Anambra':['South East'],'Imo':['South East'],'Enugu':['South East'],
        'Ebonyi':['South East'],'Abia':['South East'],
        'Kano':['North West'],'Kaduna':['North West'],'Katsina':['North West'],
        'Sokoto':['North West'],'Zamfara':['North West'],'Kebbi':['North West'],'Jigawa':['North West'],
        'Borno':['North East'],'Yobe':['North East'],'Adamawa':['North East'],
        'Gombe':['North East'],'Bauchi':['North East'],'Taraba':['North East'],
        'FCT':['North Central'],'Niger':['North Central'],'Benue':['North Central'],
        'Kogi':['North Central'],'Kwara':['North Central'],'Plateau':['North Central'],'Nasarawa':['North Central']
    }
    state_list = list(states_regions.keys())
    state_weights = [25,5,6,3,3,2,7,4,3,2,3,2,4,3,3,1,2,5,5,3,2,2,2,2,3,2,2,2,2,2,8,2,2,2,2,2,2]
    sw = np.array(state_weights[:len(state_list)], dtype=float); sw/=sw.sum()

    clusters = ['Alpha','Beta','Gamma','Delta','Epsilon','Zeta','Eta','Theta','Iota','Kappa',
                'Lambda','Mu','Nu','Xi','Omicron','Pi','Rho','Sigma','Tau','Upsilon']
    stores = [f'Store {chr(65+i)}' for i in range(26)] + [f'Store {i}' for i in range(1,15)]

    first_names = ['Adebayo','Chukwuemeka','Fatima','Blessing','Musa','Ngozi','Tunde',
                   'Amina','Oluwaseun','Chinwe','Ibrahim','Aisha','Emeka','Yetunde',
                   'Abdullahi','Chidinma','Olumide','Hauwa','Seun','Obiageli',
                   'Taiwo','Kehinde','Babatunde','Nkechi','Yusuf','Adunola','Garba',
                   'Uchenna','Sola','Precious','Ahmed','Grace','James','Mary','John',
                   'Samuel','Daniel','Emmanuel','Victor','Patience','Sunday','Mercy',
                   'Paul','Faith','Peter','Hope','Michael','Joy','Joseph','Comfort']
    last_names = ['Adeyemi','Okonkwo','Musa','Okafor','Ibrahim','Adeleke','Nwachukwu',
                  'Abubakar','Olawale','Eze','Mohammed','Obi','Adebisi','Nwosu','Danladi',
                  'Oduya','Bello','Chukwu','Salami','Nwankwo','Yusuf','Ogundele','Umar',
                  'Ikechukwu','Babangida','Adekunle','Onyeka','Garba','Oyelaran','Nwofor',
                  'Afolabi','Obiora','Hassan','Alabi','Onwudiwe','Adesanya','Lawal']

    mdas = ['Federal Ministry of Finance','Federal Ministry of Education','Federal Ministry of Health',
            'National Youth Service Corps (NYSC)','Federal & State University',
            'Federal Ministry of Defence','National Space Research And Development Agency',
            'National Assembly','Ministry Of Defence','Federal Civil Service Commission',
            'National Judicial Council','Central Bank Of Nigeria','Federal Road Safety Corps',
            'Nigerian Army','Nigerian Police Force','Nigerian Navy','Nigerian Air Force',
            'Federal Ministry of Agriculture','Federal Ministry of Works']

    device_names = ['Samsung Galaxy A54','iPhone 13','Tecno Spark 20','Infinix Hot 40',
                    'Samsung Galaxy S23','iPhone 14 Pro','HP Laptop 15','Dell Inspiron 15',
                    'Lenovo IdeaPad','Tecno Camon 20','Xiaomi Redmi Note 12','iPhone 12',
                    'Samsung Galaxy A34','Oppo A57','Vivo Y36','MacBook Air M2']

    officers = [f'{fn} {ln}' for fn,ln in zip(
        random.choices(first_names,k=30), random.choices(last_names,k=30))]
    mbe_names = [f'{fn} {ln}' for fn,ln in zip(
        random.choices(first_names,k=60), random.choices(last_names,k=60))]

    channels = np.random.choice(
        ['Salary Credit','Asset Finance','Retail Credit','Mobile Advance'],
        size=n, p=[0.38,0.35,0.20,0.07])

    # Financial Parameters by Channel 
    channel_params = {
        'Salary Credit':  {'min':500000,'max':1500000,'rate':0.075,'tenures':[12,18,24],'ir':0.075},
        'Asset Finance':   {'min':50000, 'max':600000, 'rate':0.085,'tenures':[6,9,12],  'ir':0.085},
        'Retail Credit':   {'min':50000, 'max':200000, 'rate':0.090,'tenures':[6,9,12],  'ir':0.090},
        'Mobile Advance':  {'min':30000, 'max':150000, 'rate':0.080,'tenures':[3,6,9],   'ir':0.080},
    }

    records = []
    for i in range(n):
        ch   = channels[i]
        p    = channel_params[ch]
        amt  = round(np.random.choice(np.arange(p['min'],p['max']+1,5000)), -3)
        rate = p['ir']
        ten  = random.choice(p['tenures'])
        mon_prin = round(amt/ten, 2)
        mon_int  = round(amt*rate, 2)
        mon_rep  = round(mon_prin+mon_int, 2)
        tot_exp  = round(mon_rep*ten, 2)

        # Dates
        max_start_days = (today - date(2023,1,1)).days - ten*30
        start_offset = random.randint(0, max(1, max_start_days))
        val_date  = date(2023,1,1) + timedelta(days=start_offset)
        rep_start = val_date + timedelta(days=30)
        mat_date  = val_date + timedelta(days=ten*30)

        # Repayment progress
        days_elapsed = (today - rep_start).days
        max_repaid   = min(ten, max(0, int(days_elapsed/30)))

        # Status and DPD
        rand_status = random.random()
        if mat_date < today:
            if rand_status < 0.82: status='Completed'; dpd=0; repaid_cnt=ten
            elif rand_status < 0.92: status='Defaulted'; dpd=random.randint(180,360); repaid_cnt=random.randint(0,ten//2)
            else: status='Active'; dpd=random.randint(30,180); repaid_cnt=random.randint(ten//2,ten-1)
        else:
            if rand_status < 0.62: status='Active'; dpd=0; repaid_cnt=max_repaid
            elif rand_status < 0.75: status='Active'; dpd=random.randint(1,30); repaid_cnt=max(0,max_repaid-1)
            elif rand_status < 0.84: status='Active'; dpd=random.randint(31,90); repaid_cnt=max(0,max_repaid-2)
            elif rand_status < 0.91: status='Active'; dpd=random.randint(91,180); repaid_cnt=max(0,max_repaid-3)
            else: status='Defaulted'; dpd=random.randint(180,360); repaid_cnt=max(0,max_repaid-4)

        # Financial calculations
        prin_repaid = round(mon_prin*repaid_cnt,2)
        int_repaid  = round(mon_int*repaid_cnt,2)
        tot_paid    = round(prin_repaid+int_repaid,2)
        missed      = ten-repaid_cnt if status!='Completed' else 0
        prin_arr    = round(mon_prin*missed,2) if dpd>0 else 0
        int_arr     = round(mon_int*missed,2)  if dpd>0 else 0
        tot_arr     = round(prin_arr+int_arr,2)
        gross_loan  = round(max(0,amt-prin_repaid),2)
        par_prin    = gross_loan if dpd>30 else 0
        outstanding = round(max(0,tot_exp-tot_paid),2)
        wallet_bal  = round(random.uniform(0,50000),2)

        # Classification
        if dpd==0:       cls_curr='Performing';   cls_prev='Performing'
        elif dpd<=30:    cls_curr='Pass & Watch';  cls_prev='Performing'
        elif dpd<=90:    cls_curr='Substandard';   cls_prev='Pass & Watch'
        elif dpd<=180:   cls_curr='Doubtful';      cls_prev='Substandard'
        else:            cls_curr='Lost';           cls_prev='Doubtful'
        cls_no = {'Performing':1,'Pass & Watch':2,'Substandard':3,'Doubtful':4,'Lost':5}[cls_curr]

        st    = np.random.choice(state_list, p=sw)
        reg   = states_regions[st][0]
        clu   = random.choice(clusters)
        store = random.choice(stores)
        off   = random.choice(officers)
        mbe   = random.choice(mbe_names)
        mda   = random.choice(mdas) if ch=='Salary Credit' else 'N/A'
        dev   = random.choice(device_names) if ch in ['Asset Finance','Mobile Advance'] else 'N/A'
        dev_p = round(amt*0.85,-3) if dev!='N/A' else 0

        recent_pay = round(mon_rep*random.uniform(0.8,1.2),2) if repaid_cnt>0 else 0
        recent_dt  = (rep_start+timedelta(days=repaid_cnt*30)).strftime('%d-%b-%y') if repaid_cnt>0 else 'N/A'

        records.append({
            'report_date':       today.strftime('%d-%b-%y'),
            'Loan ID':           f'LO{random.randint(1000000,9999999)}',
            'Customer_name':     f'{random.choice(first_names)} {random.choice(last_names)}',
            'store_name':        store,
            'region_name':       reg,
            'State':             st,
            'Cluster':           clu,
            'device_imei':       'N/A',
            'device_name':       dev,
            'device_price':      dev_p,
            'Loan Status':       status,
            'officer':           off,
            'MBE Name':          mbe,
            'Partner/MDA':       mda,
            'service':           ch,
            'Channel':           ch,
            'Value Date':        val_date.strftime('%d-%b-%y'),
            'Repayment Start Date': rep_start.strftime('%d-%b-%y'),
            'Maturity Date':     mat_date.strftime('%d-%b-%y'),
            'interest_rate':     rate*100,
            'Loan Tenure':       ten,
            'tenure_repaid_count':repaid_cnt,
            'Disbursed Amount':  amt,
            'monthly_principal': mon_prin,
            'monthly_interest':  mon_int,
            'monthly_repayment': mon_rep,
            'total_expected_amount': tot_exp,
            'outstanding_amount':    outstanding,
            'principal_repaid':  prin_repaid,
            'interest_repaid':   int_repaid,
            'total_paid':        tot_paid,
            'wallet_balance':    wallet_bal,
            'recent_payment_amount': recent_pay,
            'recent_payment_date':   recent_dt,
            'principal_arrears': prin_arr,
            'interest_arrears':  int_arr,
            'total_arrears':     tot_arr,
            'Gross_loan':        gross_loan,
            'adjusted_gross_loan':gross_loan,
            'PAR Principal':     par_prin,
            'previous_classification': cls_prev,
            'Current Classification':  cls_curr,
            'classification_no': cls_no,
            'dpd':               dpd,
            # Recovery fields
            'Overdue Under Recovery': tot_arr if dpd>0 else 0,
            'Recovery Rate':         f"{round(tot_paid/tot_exp*100,1)}%" if tot_exp>0 else '0.0%',
            'ACTUAL_INFLOW_TODAY':   recent_pay if today.strftime('%d-%b-%y')==recent_dt else 0,
        })

    df = pd.DataFrame(records)
    # Remove duplicate Loan IDs
    df['Loan ID'] = [f'LO{str(1000000+i).zfill(7)}' for i in range(len(df))]
    return df

if __name__ == '__main__':
    print("Generating 40,000 synthetic loan records...")
    df = generate_loan_data(40000)
    out = '/mnt/user-data/outputs/loan_portfolio_data.csv'
    df.to_csv(out, index=False)
    print(f"Saved: {out}")
    print(f"Shape: {df.shape}")
    print(f"\nChannel distribution:\n{df['Channel'].value_counts().to_string()}")
    print(f"\nClassification distribution:\n{df['Current Classification'].value_counts().to_string()}")
    print(f"\nStatus distribution:\n{df['Loan Status'].value_counts().to_string()}")
    print(f"\nKey totals:")
    print(f"  Total Disbursed: ₦{df['Disbursed Amount'].sum()/1e9:.2f}B")
    print(f"  Total Expected:  ₦{df['total_expected_amount'].sum()/1e9:.2f}B")
    print(f"  Total Repaid:    ₦{df['total_paid'].sum()/1e9:.2f}B")
    print(f"  Total Arrears:   ₦{df['total_arrears'].sum()/1e9:.2f}B")
