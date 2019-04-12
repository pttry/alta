
#TEST FINAL
i=0
#Domestic Use
            # Use at delivered prices (including margins)
            ##spread total
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(tradmar).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = margin.fillna(0)
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
use_bp=use_bp-use_bp_i
use_bp_exp=use_bp["Exp"]  
            #dom        
own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
u = np.matrix(use_bp)
use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
cor=make2.sum(axis=1)-use_bp.sum(axis=1)
exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
use_bp["Exports regional"] = exp_dom
#Inventories
stocks=stocks_obj["array"][:,i]
s=pd.DataFrame(stocks)
stocks=s.transpose()
stocks.index=["Stocks"]
stocks.columns=make_obj["sets"][1]["dim_desc"]
inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
inv=inv0.sum(axis=1)
use_bp["Inventories"]=inv
use_bp_dom=use_bp

#Regional Use
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(tradmar).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = margin.fillna(0)
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
use_bp=use_bp-use_bp_i  
            #regions
own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
u = np.matrix(use_bp)
use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
use_bp["Exports regional"] = 0
            #use_bp["Exp"] = 0
use_bp["Inventories"]=0
use_bp_reg=use_bp

#USE foreign
use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
use_bp = use_dp - use_dp_tr
use_bp["Exports regional"] = 0
use_bp["Inventories"]=0
use_bp_for=use_bp


#USE total

use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(tradmar).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
use_bp_total=use_bp
            #spread imports
use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = margin.fillna(0)
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
use_bp=use_bp-use_bp_i
use_bp_exp=use_bp["Exp"]  
            #dom        
own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
u = np.matrix(use_bp)
use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
use_bp_d= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
use_bp_total= pd.DataFrame(use_bp_total, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"])
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
cor=make2.sum(axis=1)-use_bp_d.sum(axis=1)
exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
use_bp_total["Exports regional"] = exp_dom
#Inventories
stocks=stocks_obj["array"][:,i]
s=pd.DataFrame(stocks)
stocks=s.transpose()
stocks.index=["Stocks"]
stocks.columns=make_obj["sets"][1]["dim_desc"]
inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
inv=inv0.sum(axis=1)
use_bp_total["Inventories"]=inv

check=use_bp_total-use_bp_dom-use_bp_for-use_bp_reg
for k in check.columns.tolist():
        if (abs(check[k]) < 0.001).all():
                print("For use ", k, "the difference IS zero")
        else:
                print("For use ", k, "the difference NOT zero")



