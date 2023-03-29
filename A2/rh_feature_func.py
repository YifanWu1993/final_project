#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 14:59:33 2023

@author: dingzujian
"""

import time
import sys
import os

import logging
import json
import traceback
from typing import Union, List
from datetime import datetime
from dateutil import parser
import xmltodict
import pandas as pd
import numpy as np
import time

func_dict = {
    'sum':sum,
    'max':max,
    'min':min,
    'mean':np.mean,
    'std':np.std,
    'count':len,
    'median':np.median
    }

loan_dict = {
    'mort':['11','12','13'],
    'vehicle':['21'],
    'mort_vehicle':['11','12','13','21'],
    'biz':['41'],
    'con':['91'],
    'large_installment':['82']
    #'guarantee':['']
    }

special_dict = {
    'extend_reduce':['展期','债务减免'],
    'bad':["担保人（第三方）代偿","以资抵债","强制平仓，未结清","司法追偿"]
    }

def specials_early_end(x):
    if_early_end = 0
    for each in x:
        if each['tradeTypeOri'] == '5':
            if_early_end = 1
        else:
            continue
    return if_early_end




def special_oth(x,special_list):
    #global special_list
    if_special = 0
    for each in x:
        if each['tradeType'] in special_list:
            if_special = 1
        else:
            continue
    return if_special
    
    

lvl_map_dict = {'G':13,'D':13,'Z':13,'B':13,'M':13,'7':12,'6':11,'5':10,'4':9,'3':8,'2':7,'1':6,'C':5,'N':4,'A':3,'*':2,'#':1}
lvl_map_rev = {13: 'M', 12: '7', 11: '6', 10: '5', 9: '4', 8: '3', 7: '2', 6: '1', 5: 'C', 4: 'N', 3: 'A', 2: '*', 1: '#'}



def rh_feature_func(body):
    tot_dict = {'rpt_tim': get_value('header,messageHeader,reportCreateTime', body).replace(':', '-')[:10]}
    # tot_dict['qry_is_weekend'] = 'y' if datetime.strptime(tot_dict['rpt_tim'], '%Y-%m-%d').weekday() >= 5 else 'n'


    # 个人信息类
    personal_var = personal_info(body, tot_dict['rpt_tim'])
    tot_dict.update(personal_var)

    # 还款责任类
    hkzr_var = xghkzr_info(body)
    tot_dict.update(hkzr_var)


    # 公共信息类
    acc_fund_var = public_info(body)
    tot_dict.update(acc_fund_var)
    
    #借贷信息类
    tot_info_var = tot_info(body, tot_dict['rpt_tim'])
    tot_dict.update(tot_info_var)
    tot_df = pd.DataFrame([tot_dict]).fillna(-999)

    return tot_df



def personal_info(body,rpt_tim):
    job_df = pd.DataFrame(body['personalInfo']['professional'],columns = ['employer', 'employerAttr', 'employerAddress', 
                                                                          'employerTelephone','occupation', 'industry', 
                                                                          'duty', 'title', 'startYear', 'getTime']).fillna(np.nan)
    mobile_df = pd.DataFrame(body['personalInfo']['identity']['mobiles'],columns = ['mobile','mobileUpdateTime'])
    residence_df = pd.DataFrame(body['personalInfo']['residence'],columns = ['getTime','address','residenceType','homeTelephone'])
    job_df['rpt_tim'] = rpt_tim
    mobile_df['rpt_tim'] = rpt_tim
    
    job_df['open_to_now'] = (pd.to_datetime(job_df['rpt_tim']) - pd.to_datetime(job_df['startYear'])).map(lambda x: int(x.days) if str(x) != 'NaT' else np.nan)
    mobile_df['open_to_now'] = (pd.to_datetime(job_df['rpt_tim']) - pd.to_datetime(job_df['startYear'])).map(lambda x: int(x.days) if str(x) != 'NaT' else np.nan)
    out_dict = {}
    for day in [180,360,1080,1800]:
        job_df_tmp = job_df[job_df['open_to_now'] <= day]
        out_dict['indv_his_emp_ind_cnt_{window}d'.format(window=str(day))] = len(job_df_tmp['industry'].unique())
        out_dict['indv_his_emp_com_cnt_{window}d'.format(window=str(day))] = len(job_df_tmp['employer'].unique())
        mobile_df_tmp = mobile_df[mobile_df['open_to_now'] <= day]
        out_dict['indv_his_mob_cnt_{window}d'.format(window=str(day))] = len(mobile_df_tmp['mobile'].unique())
        
    out_dict['indv_his_emp_ind_cnt'] = len(job_df['industry'].unique())
    out_dict['indv_his_emp_ind_unk_cnt'] = job_df[(job_df['industry'].map(str).str.contains('9')) & ~(job_df['employer'].map(str).str.contains('个体'))]['industry'].count()
    out_dict['indv_his_emp_duty_cnt'] = len(job_df['duty'].unique())
    out_dict['indv_his_emp_duty_unk_cnt'] = job_df[(job_df['duty'].map(str).str.contains('9')) & ~(job_df['employer'].map(str).str.contains('个体'))]['industry'].count()
    out_dict['indv_his_emp_job_cnt'] = len(job_df['occupation'].unique())
    out_dict['indv_his_emp_job_unk_cnt'] = job_df[(job_df['occupation'].map(str).str.contains('Z')) & ~(job_df['employer'].map(str).str.contains('个体'))]['industry'].count()
    out_dict['indv_his_emp_duty_mean'] = job_df['duty'].map(float).mean()
    out_dict['indv_his_emp_duty_max'] = job_df['duty'].map(float).min()
    out_dict['indv_his_emp_large_city_gov_com_cnt'] = job_df[(job_df['employerAddress'].map(str).str.contains(r'北京｜上海|广州|深圳',regex=True)) | (job_df['employerAttr'] == '10')]['employerAttr'].count()
    out_dict['indv_his_emp_large_city_fori_com_cnt'] = job_df[(job_df['employerAddress'].map(str).str.contains(r'北京｜上海|广州|深圳',regex=True)) | (job_df['employerAttr'] == '30')]['employerAttr'].count()
    out_dict['indv_his_emp_large_city_mort_res_cnt'] = residence_df[(residence_df['address'].map(str).str.contains(r'北京｜上海|广州|深圳',regex=True)) | (residence_df['residenceType'].isin(['1','2','11']))]['address'].count()
    out_dict['indv_his_emp_big_city_mort_res_cnt'] = residence_df[(residence_df['address'].map(str).str.contains(r'北京|上海|广州|深圳|厦门|杭州|三亚|南京|陵水|福州|珠海|天津|东莞|宁波|苏州',regex=True)) | (residence_df['residenceType'].isin(['1','2','11']))]['address'].count()
    return out_dict

def xghkzr_info(body):
    hkzr_df = pd.DataFrame(body.get('repayDetail'),columns = ['loanIdentityType', 'manageOrgType', 'manageOrg', 'busiType', 'opnDte', 'dueDte', 'hkzrType', 
                                                          'hkzrAccountNo', 'hkzrAmount', 'hkzrcurrency', 'hkzrbalance', 'hkzrclass5StateOri', 'hkzrAccountType', 
                                                          'hkzrRepayState', 'hkzrDueMths', 'hkzrRptDte'])
    hkzr_df = hkzr_df.fillna(np.nan)
    hkzr_df['hkzrclass5StateOri'] = hkzr_df['hkzrclass5StateOri'].map(lambda x:np.nan if x == '9' else x)
    try:
        hkzr_df['hkzr_overdue_combine'] = hkzr_df[['hkzrDueMths','hkzrRepayState']].apply(lambda x:x['hkzrDueMths'] if str(x['hkzrDueMths']) != 'nan' else x['hkzrRepayState'],axis=1)
    except:
        hkzr_df['hkzr_overdue_combine'] = np.nan
    hkzr_df['hkzr_mapping'] = hkzr_df['hkzr_overdue_combine'].map(lvl_map_dict)
    out_dict = {}
    out_dict['xghkzr_bzr_cnt'] = hkzr_df[hkzr_df['hkzrType'] == '2']['loanIdentityType'].count()
    
    for each in ['sum','max','min','mean','std']:
        aggfunc = func_dict[each]
        try:
            out_dict['xghkzr_bzr_repay_amt_{func}'.format(func=each)] = aggfunc(hkzr_df[hkzr_df['hkzrType'] == '2']['hkzrAmount'].map(float))
        except:
            out_dict['xghkzr_bzr_repay_amt_{func}'.format(func=each)] = np.nan
        try:
            out_dict['xghkzr_bzr_repay_blc_{func}'.format(func=each)] = aggfunc(hkzr_df[hkzr_df['hkzrType'] == '2']['hkzrbalance'].map(float))
        except:
            out_dict['xghkzr_bzr_repay_blc_{func}'.format(func=each)] = np.nan
            
        try:
            out_dict['xghkzr_bzr_repay_5_class_{func}'.format(func=each)] = aggfunc(hkzr_df[hkzr_df['hkzrType'] == '2']['hkzrclass5StateOri'].map(float))
        except:
            out_dict['xghkzr_bzr_repay_5_class_{func}'.format(func=each)] = np.nan
        try:
            out_dict['xghkzr_com_repay_5_class_{func}'.format(func=each)] = aggfunc(hkzr_df[~hkzr_df['hkzrDueMths'].isna()]['hkzrclass5StateOri'].map(float))
        except:
            out_dict['xghkzr_com_repay_5_class_{func}'.format(func=each)] = np.nan
            
    try:
        
        tmp_status = max(hkzr_df[hkzr_df['hkzrType'] == '2']['hkzr_mapping'].map(float))
        #print (tmp_status)
        try:
            result = float(lvl_map_rev[tmp_status])
        except:
            result = lvl_map_rev[tmp_status]
             
        out_dict['xghkzr_bzr_repay_status_{func}'.format(func='max')] = result
        
    except:
        out_dict['xghkzr_bzr_repay_status_{func}'.format(func='max')] = np.nan
        
    return out_dict


def public_info(body):
    ad_pu_df = pd.DataFrame(body['publicInfo']['administrativePunishment'],columns = ['orgnization','content','amount','effectiveDate','endDate','reconsiderationResult'])
    acc_df = pd.DataFrame(body['publicInfo']['accFund'],columns = ['area', 'registerDate', 'firstMonth', 'toMonth', 'state', 'pay', 'ownPercent', 'comPercent', 'organname', 'getTime'])
    no_credit_df = pd.DataFrame(body['summary_info']['notCreditTrade'],columns = ['type','account','amount'])
    
    out_dict = {}
    out_dict['admin_punish_drug_bet_gamb_cnt'] = ad_pu_df[(ad_pu_df['content'].str.contains('赌博')) | (ad_pu_df['content'].str.contains('吸毒'))]['content'].count()
    out_dict['no_credit_amount_sum'] = no_credit_df['amount'].sum()
    try:
        out_dict['acc_fund_latest_area'] = acc_df.loc[np.argmax(acc_df['registerDate']),'area']
    except:
        out_dict['acc_fund_latest_area'] = np.nan
    out_dict['acc_fund_area_cnt'] = len(acc_df['area'].unique())
    return out_dict

def tot_info(body,rpt_tim):
    out_dict = {}
    credit_columns = ['account',
 'account_type_ori',
 'account_type',
 'org_type_ori',
 'org_type',
 'org_no',
 'account_label',
 'no',
 'openDate',
 'endDate',
 'loanAmount',
 'currencyOri',
 'currency',
 'loanTypeOri',
 'loanType',
 'guaranteeOri',
 'guarantee',
 'shareAmount',
 'repayTypeOri',
 'repayType',
 'loanFrequencyOri',
 'loanFrequency',
 'loanTerm',
 'loanLabel',
 'loan_method',
 'loan_repay_status',
 'stateOri',
 'state',
 'class5StateOri',
 'class5State',
 'balance',
 'recentPayDate',
 'closeDate',
 'outMonth',
 'repayStatus',
 'report_date',
 'actualPaymentAmount',
 'remainPaymentCyc',
 'scheduledPaymentAmount',
 'scheduledPaymentDate',
 'month',
 'usedCreditLimitAmount',
 'highCreditBalance',
 'usedHighestAmount',
 'billDate',
 'currOverdueCyc',
 'currOverdueAmount',
 'latest6MonthUsedAvgAmount',
 'overdue31To60Amount',
 'overdue61To90Amount',
 'overdue91To180Amount',
 'overdueOver180Amount',
 'repayRecord',
 'specials',
 'largeCreditCnt',
 'largeCreditLimit',
 'largeStartDate',
 'largeEndDate',
 'largeUsedCreditLimit']
    
    qry_columns = ['queryDate', 'querier', 'querierTypeOri', 'querierType','queryReasonOri', 'queryReason']
    qry_df = pd.DataFrame(body['queryRecord'],columns=qry_columns)
    qry_df['rpt_tim'] = rpt_tim
    qry_df['qry_to_now'] = (pd.to_datetime(qry_df['rpt_tim']) - pd.to_datetime(qry_df['queryDate'])).map(lambda x: int(x.days) if str(x) != 'NaT' else np.nan)
    loan_df = pd.DataFrame(body['creditDetail']['loan'],columns=credit_columns)
    loan_card_df = pd.DataFrame(body['creditDetail']['loan_card'],columns=credit_columns)
    tot_df = loan_df.append(loan_card_df)
    tot_df['rpt_tim'] = rpt_tim
    tot_df['open_to_now'] = (pd.to_datetime(tot_df['rpt_tim']) - pd.to_datetime(tot_df['openDate'])).map(lambda x: int(x.days) if str(x) != 'NaT' else np.nan)
    tot_df['schedual_to_repay'] = (pd.to_datetime(tot_df['recentPayDate']) - pd.to_datetime(tot_df['scheduledPaymentDate'])).map(lambda x: int(x.days) if str(x) != 'NaT' else np.nan)
    tot_df['if_early_end'] = tot_df['specials'].map(specials_early_end)
    tot_df['oth_loan_flag'] = tot_df['loanTypeOri'].map(lambda x:1 if x not in ['11','12','13','21'] else 0)
    tot_df['mort_flag'] = tot_df['loanTypeOri'].map(lambda x:1 if x in ['11','12','13'] else 0)
    
    for day in [30,90,180,360,720,1440,1800]:
        for account_type in ['C1','D1','R1','R2','R3','R4']:
            for cur in ['CNY','USD']:
                df_tmp = tot_df[(tot_df['open_to_now'] <= day) & (tot_df['account_type_ori'] == account_type) & (tot_df['currencyOri'] == cur)]
                #机构数
                out_dict['tot_{account_type}_{cur}_org_cnt_{day}d'.format(account_type=account_type, cur=cur, day=day)] = len(df_tmp['org_no'].dropna().unique())
                for func in func_dict.keys():
                    #print (func)
                    aggfunc = func_dict[func]
                    for target in ['loanAmount','balance']:                                                
                    #其他聚合函数
                        try:
                            out_dict['tot_{account_type}_{cur}_{target}_{func}_{day}d'.format(account_type=account_type, cur=cur, day=day, func=func, target=target)] = aggfunc(df_tmp[target].map(float))
                        except:
                            out_dict['tot_{account_type}_{cur}_{target}_{func}_{day}d'.format(account_type=account_type, cur=cur, day=day, func=func, target=target)] = np.nan
                            
    
    amount_arry = [10000, 30000, 50000, 100000,200000,300000,500000]
    for each in amount_arry:
        df_tmp = tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['loanAmount'].map(float) >= each)]
        out_dict['loan_card_amount_{amount}_org_cnt'.format(amount = each)] = len(df_tmp['org_no'].dropna().unique())
        out_dict['loan_card_amount_{amount}_open_date_max'] = df_tmp['openDate'].max()
        out_dict['loan_card_amount_{amount}_open_date_min'] = df_tmp['openDate'].min()
        
    amount_arry = [50000, 100000, 250000, 500000,1000000,2000000]
    for each in amount_arry:
        for lon_type in loan_dict.keys():
            if lon_type == 'mort_vehicle':
                continue
            df_tmp = tot_df[(tot_df['loanTypeOri'].isin(loan_dict[lon_type])) & (tot_df['loanAmount'].map(float) >= each)]
            out_dict['loan_{lon_type}_{amount}_account_cnt'.format(lon_type = lon_type,amount=each)] = len(df_tmp['account'].dropna().unique())
        df_tmp = tot_df[(tot_df['guaranteeOri'] == '2') & (tot_df['loanAmount'].map(float) >= each)]
        out_dict['loan_guarantee_{amount}_account_cnt'.format(amount = each)] = len(df_tmp['account'].dropna().unique())
        
        
            
            
            #out_dict['loan_card_amount_{amount}_org_cnt'.format(amount = each)] = len(df_tmp['org_no'].unique())
            #out_dict['loan_card_amount_{amount}_open_date_max'] = df_tmp['openDate'].max()
            #out_dict['loan_card_amount_{amount}_open_date_min'] = df_tmp['openDate'].min()
    
    
    
        #out_dict['loan_card_amount_{amount}_org_cnt'.format(amount = each)]
    for day in [1,2,3,4]:
        out_dict['tot_rep_sch_day_diff_{day}d_act_cnt'] = len(tot_df[(tot_df['schedual_to_repay'] > day) & (tot_df['state'] == '结清')]['account'].dropna().unique())
        
    for lon_type in loan_dict.keys():
        for day in [30,90,180,360,720,1440,1800]:
            if lon_type == 'mort_vehicle':
                df_tmp = tot_df[~(tot_df['loanTypeOri'].isin(loan_dict[lon_type])) & (tot_df['if_early_end'] == 1) & (tot_df['open_to_now'] <= day)]
                for func in func_dict.keys():
                    #print (func)
                    aggfunc = func_dict[func]
                    for target in ['loanAmount']:                                                
                        #其他聚合函数
                        try:
                            out_dict['loan_{lon_type}_{target}_{func}_{day}d'.format(lon_type=lon_type, day=day, func=func, target=target)] = aggfunc(df_tmp[target].map(float))
                        except:
                            out_dict['loan_{lon_type}_{target}_{func}_{day}d'.format(lon_type=lon_type, day=day, func=func, target=target)] = np.nan
            else:
                df_tmp = tot_df[(tot_df['loanTypeOri'].isin(loan_dict[lon_type])) & (tot_df['if_early_end'] == 1) & (tot_df['open_to_now'] <= day)]
                for func in func_dict.keys():
                    #print (func)
                    aggfunc = func_dict[func]
                    for target in ['loanAmount']:                                                
                        #其他聚合函数
                        try:
                            out_dict['loan_{lon_type}_{target}_{func}_{day}d'.format(lon_type=lon_type, day=day, func=func, target=target)] = aggfunc(df_tmp[target].map(float))
                        except:
                            out_dict['loan_{lon_type}_{target}_{func}_{day}d'.format(lon_type=lon_type, day=day, func=func, target=target)] = np.nan
                            

    df_mort_veh = tot_df[(tot_df['loanTypeOri'].isin(loan_dict[lon_type]))]
    df_d1 = tot_df[(tot_df['account_type'] == 'D1')]
    out_dict['loan_mort_vech_d1_ratio'] = df_mort_veh['latest6MonthUsedAvgAmount'].sum()/(df_d1['latest6MonthUsedAvgAmount'].sum() + 0.0001)
    for day in [30,90,180,360]:
        #贷记卡申请成功比例
        loan_card_org_cnt = len(tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['open_to_now'] <= day)]['org_no'].dropna().unique())
        loan_card_qry_cnt = len(qry_df[(qry_df['queryReason'] == '信用卡审批') & (qry_df['qry_to_now'] <= day)]['querier'].dropna().unique())
        out_dict['loan_card_suc_ratio_{day}d'.format(day=str(day))] = loan_card_org_cnt/(loan_card_qry_cnt+0.00001)
        
        #贷记卡申请成功比例
        loan_org_cnt = len(tot_df[~(tot_df['account_type_ori'].isin(['R2','R3'])) & (tot_df['open_to_now'] <= day)]['org_no'].dropna().unique())
        loan_qry_cnt = len(qry_df[(qry_df['queryReason'] == '贷款审批') & (qry_df['qry_to_now'] <= day)]['querier'].dropna().unique())
        out_dict['loan_suc_ratio_{day}d'.format(day=str(day))] = loan_card_org_cnt/(loan_qry_cnt + 0.00001)
        
    for special in special_dict:
        special_list = special_dict[special]
        out_dict['tot_special_tarde_{special}_cnt'.format(special=special)] = tot_df['specials'].apply(special_oth,**{'special_list':special_list}).count()
        
    #未激活贷记卡数
    out_dict['loan_card_not_act_account_cnt'] = len(tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['state'] == '未激活')]['account'].dropna().unique())
    
    for day in [90,180,360,720]:
        out_dict['loan_card_not_act_account_cnt_{day}d'] = len(tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['state'] == '未激活') & (tot_df['open_to_now'] <= day)]['account'].dropna().unique())
        df_tmp = tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['state'] == '未激活') & (tot_df['open_to_now'] <= day)]
        for func in func_dict.keys():
            #print (func)
            aggfunc = func_dict[func]
            for target in ['loanAmount']:
                try:
                    out_dict['loan_card_not_act_{target}_{func}_{day}d'.format(day=day, func=func, target=target)] = aggfunc(df_tmp[target].map(float))
                except:
                    out_dict['loan_card_not_act_{target}_{func}_{day}d'.format(day=day, func=func, target=target)] = np.nan
        
        df_tmp = tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['state'] != '未激活') & (tot_df['open_to_now'] <= day)]
        for func in func_dict.keys():
            #print (func)
            aggfunc = func_dict[func]
            for target in ['loanAmount']:
                try:
                    out_dict['loan_card_act_{target}_{func}_{day}d'.format(day=day, func=func, target=target)] = aggfunc(df_tmp[target].map(float))
                except:
                    out_dict['loan_card_act_{target}_{func}_{day}d'.format(day=day, func=func, target=target)] = np.nan
    
    #3/6信用卡信息
    for day in [90,180]:
        df_tmp = tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['open_to_now'] <= day) & (tot_df['repayRecord'].map(lambda x:len(x)) > 0)]
        for func in func_dict.keys():
            #print (func)
            aggfunc = func_dict[func]
            for target in ['loanAmount']:
                try:
                    out_dict['loan_card_repayed_{target}_{func}_{day}d'.format(day=day, func=func, target=target)] = aggfunc(df_tmp[target].map(float))
                except:
                    out_dict['loan_card_repayed_{target}_{func}_{day}d'.format(day=day, func=func, target=target)] = np.nan
                    
    for day in [0,1,3]:
        #贷记卡申请成功比例
        #loan_card_org_cnt = len(tot_df[(tot_df['account_type_ori'] == 'R2') & (tot_df['open_to_now'] <= day)]['org_no'].dropna().unique())
        loan_card_qry_cnt = qry_df[(qry_df['queryReason'] == '信用卡审批') & (qry_df['qry_to_now'] <= day)]['querier'].dropna().count()
        out_dict['qry_loan_card_qry_cnt_{day}d'.format(day=str(day))] = loan_card_qry_cnt
        
        #贷记卡申请成功比例
        loan_qry_cnt = qry_df[(qry_df['queryReason'] == '贷款审批') & (qry_df['qry_to_now'] <= day)]['querier'].dropna().count()
        out_dict['qry_loan_qry_cnt_{day}d'.format(day=str(day))] = loan_qry_cnt
        
        loan_qry_cnt = qry_df[(qry_df['qry_to_now'] <= day)]['querier'].dropna().count()
        out_dict['qry_tot_qry_cnt_{day}d'.format(day=str(day))] = loan_card_qry_cnt


    cur_ovd_amt_r2 = []
    for i in get_value('creditDetail,loan_card',body):
        if get_value('account_type_ori',i) in ['R2'] :
            cur_ovd_amt_r2.append(float(get_value('currOverdueAmount',i,0)))
    out_dict['rules_cardoverdueamtsum'] =  sum(cur_ovd_amt_r2) if len(cur_ovd_amt_r2) != 0 else 0
    
    # D3 贷款当前逾期总额
    cur_ovd_amt_lon = []
    for i in get_value('creditDetail,loan',body):
        # 贷款当前逾期总额
        cur_ovd_amt_lon.append(float(get_value('currOverdueAmount',i,0)))
    out_dict['rules_loanoverdueamtsum'] = sum(cur_ovd_amt_lon)    
    return out_dict
                    
                
def get_value(key_str: str, obj: Union[str, dict, list], default=None, key_split: str = ','):
    """
    从json字符串或者dict或者list中获取指定key的值,key的格式为`node1,node2`
    :param key_str:
    :param obj:
    :param default:
    :param key_split:
    :return:
    """
    if empty_judge(obj):
        return default
    if isinstance(obj, str):
        obj = json.loads(obj)
    key_lst = key_str.split(key_split)
    if len(key_lst) >= 1:
        if isinstance(obj, list):
            try:
                k = int(key_lst[0])
                if k >= len(key_lst):
                    print('warning, out of list index: {0} of length {1}'.format(k, len(key_lst)))
                    return default
                if len(key_lst) == 1:
                    return obj[k]
                else:
                    return get_value('{0}'.format(key_split).join(key_lst[1:]), obj[k], default, key_split)
            except ValueError:
                raise TypeError("expect int index, actual: {0} of type {1}".format(key_lst[0], type(key_lst[0])))
        elif isinstance(obj, dict):
            if len(key_lst) == 1:
                v = obj.get(key_lst[0])
                return default if v is None else v
            else:
                return get_value('{0}'.format(key_split).join(key_lst[1:]), obj.get(key_lst[0], {}), default, key_split)
        else:
            if len(key_lst) >= 1:
                print('warning, has redundancy key: {0}'.format('{0}'.format(key_split).join(key_lst)))
            return obj
    else:
        raise ValueError("illegal key string")    
        
def empty_judge(el) -> bool:
    """
    判断元素是否为空
    >>> empty_judge(None), empty_judge(''), empty_judge(0), empty_judge(0.0)
    (True, True, True, True)
    >>> empty_judge([]), empty_judge({}), empty_judge([{}])
    (True, True, True)
    >>>empty_judge(pd.DataFrame())
    True
    >>>empty_judge(np.nan)
    True
    :param el:
    :return:
    """
    if el is None:
        return True
    elif isinstance(el, (int, float, bool, str)):
        if isinstance(el, float) and str(el) == 'nan':
            return True
        return True if not el else False
    elif isinstance(el, list):
        if not el:
            return True
        else:
            for v in el:
                if not empty_judge(v):
                    return False
            return True
    elif isinstance(el, dict):
        return True if not el else False
    elif isinstance(el, (pd.Series, pd.DataFrame)):
        return len(el) == 0
    elif pd.isnull(el):
        return True
    else:
        return False
    
    
    
if __name__ == '__main__':
    import os
    import sys
    sys.path.append('/Users/dingzujian/Desktop/未命名文件夹/文件/外部数据/人行/pboc_var(1)')
    from xml2json_v2 import *
    #file_list = os.listdir('/Users/dingzujian/Desktop/未命名文件夹/文件/外部数据/人行/xml案例')
    file_list = ['222.xml']
    
    file_list = ['0000efd1-4cb3-4d0f-8d72-4de3af07da86.xml',
'09341ea3-ec3e-41d5-b483-d6659cbff1df.xml',
'0d22fde1-3b08-479f-9a97-4faf090582c0.xml',
'0fa934ab-1d40-4f35-a17a-a5fab055fcdf.xml',
'155ded56-cecf-4775-af07-c279d540719d.xml',
'162b6ddd-3c0b-4214-9800-bdfecccd985e.xml',
'1e980187-6ea5-41e5-9133-1564f89bed6c.xml',
'30ce72d9-2a2e-458c-a488-27c031ed80e3.xml',
'4466e54f-5298-41e9-8347-638593db876c.xml',
'50f198df-5118-41bf-bb10-bfce8a82bdec.xml',
'545d41f4-5fc1-4599-9da5-f9d42eaefb4b.xml',
'54680e0d-5253-42bf-a9f9-81f1105b8570.xml',
'785f00ca-f96a-4e42-b158-8c10351818d6.xml',
'89bcec26-90df-4059-b92a-1fc7db60ffc7.xml',
'89d1f080-5bab-4aaa-a382-af8e1f6515c8.xml',
'8b132786-be26-4211-9539-0c1e064e28c4.xml',
'9a60e01c-dd18-46f9-aa65-4afe97591783.xml',
'9d249599-f0f9-49c7-8648-0b176c6ed62f.xml',
'a1f1e34a-ac3f-4b72-a66a-18aa91306661.xml',
'a597f964-2f35-4e1a-a0e9-903c923c1445.xml',
'b2fc9778-8681-4d11-b9cd-a51b1947904c.xml',
'b73c133b-a2dd-4acc-ad4b-523cf50f868a.xml',
'c341fc00-6138-496d-b4d0-f28d0db9c043.xml',
'c3e8336a-2855-48b9-9866-13e31a7d92c8.xml',
'cef0a200-33ef-4cfa-95b5-23c3c6b7a7d2.xml',
'd4d76eb5-4b7a-4214-9f32-dcd6878bf5c0.xml',
'dc138143-a422-40b3-8f2d-5c9f144ef5ba.xml',
'df8532a0-c7b4-4f73-b70d-8b3964f6461f.xml',
'e4bc86fb-9fa4-4adb-90cf-6bf36be31c44.xml',
'ec628d74-d391-4ffb-818a-8b1f86d62295.xml',
'fa4d47b8-17ad-4fed-9366-027c2f173375.xml',
'fc24a73f-5bca-4d25-8bd3-ef6c57e1b5f9.xml',
'fdbb8f11-a558-4014-9c20-cb6e45fa6776.xml',
'公积金_cd81c8c2-2ad8-4ed6-8678-9d0f4cd5d0b9.xml']
    #pre_path = '/Users/dingzujian/Desktop/未命名文件夹/文件/外部数据/人行/xml案例/'
    #pre_path = '/Users/dingzujian/Desktop/未命名文件夹/文件/外部数据/人行/pboc_var(1)/models/big_table_v3'
    total_df = pd.DataFrame()

    for each in file_list:
        #file = '/Users/dingzujian/Desktop/未命名文件夹/文件/外部数据/人行/pboc_var(1)/models/big_table_v3/'+each
        file = '/Users/dingzujian/Desktop/未命名文件夹/文件/外部数据/人行/xml案例/'+each
        #file = each
        with open(file, encoding='utf-8') as fi:
            document = fi.read()
            st = time.time()
        body = xml_to_json(document = document)
        #try:
        #    print (pd.DataFrame(body['repayDetail'])['hkzrRepayState'])
        #except:
        #    continue
        ed1 = time.time()
        res_df = rh_feature_func(body)
        total_df = total_df.append(res_df)
        #display(res_df)
        ed2 = time.time()
        print('xmltojson program time cost(ms) = ', (ed1 - st) * 1000)
        print('Just Features Time cost(ms) = ', (ed2 - ed1) * 1000)
        
    
    
    
    



    
    
            
        
            
        
        
    