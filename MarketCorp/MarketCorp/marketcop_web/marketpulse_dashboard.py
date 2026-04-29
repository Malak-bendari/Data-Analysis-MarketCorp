"""
MarketCorp Analytics Dashboard
Themes: Acid Terminal (dark) + Azure Clarity (light)
Run:
    pip install streamlit pandas numpy plotly scikit-learn anthropic pdfplumber
    streamlit run marketcorp_dashboard.py
"""

import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly .express as px 
import plotly .graph_objects as go 
import io ,warnings ,base64 
warnings .filterwarnings ("ignore")




FAVICON_SVG ="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0d0d10"/>
  <polygon points="32,8 56,20 56,44 32,56 8,44 8,20" fill="none" stroke="#b4ff47" stroke-width="3"/>
  <text x="32" y="38" text-anchor="middle" font-family="Arial Black,sans-serif"
        font-size="18" font-weight="900" fill="#b4ff47">MC</text>
</svg>"""
favicon_b64 =base64 .b64encode (FAVICON_SVG .encode ()).decode ()
favicon_uri =f"data:image/svg+xml;base64,{favicon_b64 }"




st .set_page_config (
page_title ="MarketCorp Analytics",
page_icon =favicon_uri ,
layout ="wide",
initial_sidebar_state ="expanded",
)




THEMES ={
"Acid Terminal":{
"bg":"#060608","bg1":"#0d0d10","bg2":"#131318","bg3":"#1a1a22",
"accent":"#b4ff47","accent2":"#7ab830","glow":"rgba(180,255,71,.18)",
"text":"#e8e8f0","text_dim":"#8888aa","muted":"#3a3a4a",
"red":"#ff4757","amber":"#ffa502","cyan":"#00d2ff",
"palette":["#b4ff47","#00d2ff","#ffa502","#ff4757","#a855f7","#38bdf8","#fb923c","#4ade80"],
"grad_lo":"#1a1a22","grad_hi":"#b4ff47",
"plot_bg":"#131318","plot_paper":"#131318","grid":"#3a3a4a",
"scrollbar_thumb":"#7ab830",
},
"Azure Clarity":{
"bg":"#f0f4ff","bg1":"#e4ecff","bg2":"#ffffff","bg3":"#dce6ff",
"accent":"#1a5ce8","accent2":"#3b7af7","glow":"rgba(26,92,232,.12)",
"text":"#0f1a35","text_dim":"#5567a0","muted":"#c2d0ee",
"red":"#e03e52","amber":"#d97706","cyan":"#0284c7",
"palette":["#1a5ce8","#0284c7","#6366f1","#7c3aed","#0ea5e9","#3b82f6","#8b5cf6","#06b6d4"],
"grad_lo":"#dce6ff","grad_hi":"#1a5ce8",
"plot_bg":"#ffffff","plot_paper":"#f0f4ff","grid":"#c2d0ee",
"scrollbar_thumb":"#3b7af7",
},
}




for key ,val in [("df",None ),("chat_history",[]),("pdf_text",""),
("ml_results",None ),("theme","Acid Terminal")]:
    if key not in st .session_state :
        st .session_state [key ]=val 

T =THEMES [st .session_state .theme ]




def inject_css (t ):
    st .markdown (f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Grotesk:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;600&display=swap');

:root {{
    --bg:{t ["bg"]}; --bg1:{t ["bg1"]}; --bg2:{t ["bg2"]}; --bg3:{t ["bg3"]};
    --accent:{t ["accent"]}; --accent2:{t ["accent2"]}; --glow:{t ["glow"]};
    --text:{t ["text"]}; --text-dim:{t ["text_dim"]}; --muted:{t ["muted"]};
    --red:{t ["red"]}; --amber:{t ["amber"]}; --cyan:{t ["cyan"]};
}}

html,body,[class*="css"],.stApp {{
    background:var(--bg) !important; color:var(--text) !important;
    font-family:'Space Grotesk',sans-serif !important;
}}
::-webkit-scrollbar {{width:4px;height:4px;}}
::-webkit-scrollbar-track {{background:var(--bg1);}}
::-webkit-scrollbar-thumb {{background:{t ["scrollbar_thumb"]};border-radius:2px;}}

[data-testid="stSidebar"] {{background:var(--bg1) !important;border-right:1px solid var(--muted) !important;}}
[data-testid="stSidebar"] * {{color:var(--text) !important;}}
[data-testid="stSidebarNav"] {{display:none;}}

h1,h2,h3 {{font-family:'Syne',sans-serif !important;letter-spacing:-0.03em;}}
h1 {{color:var(--accent) !important;font-weight:800 !important;font-size:2.2rem !important;}}
h2 {{color:var(--text) !important;font-weight:700 !important;}}
h3 {{color:var(--accent2) !important;font-weight:600 !important;}}

[data-testid="metric-container"] {{
    background:var(--bg2) !important; border:1px solid var(--muted) !important;
    border-radius:6px !important; padding:1rem 1.2rem !important; transition:border-color .2s;
}}
[data-testid="metric-container"]:hover {{border-color:var(--accent) !important;}}
[data-testid="stMetricLabel"] {{
    font-family:'JetBrains Mono',monospace !important; font-size:.72rem !important;
    color:var(--text-dim) !important; text-transform:uppercase; letter-spacing:.08em;
}}
[data-testid="stMetricValue"] {{
    font-family:'Syne',sans-serif !important; font-size:1.9rem !important;
    color:var(--accent) !important; font-weight:800 !important;
}}
[data-testid="stMetricDelta"] {{font-family:'JetBrains Mono',monospace !important;}}

.stButton>button {{
    background:transparent !important; border:1px solid var(--accent) !important;
    color:var(--accent) !important; font-family:'JetBrains Mono',monospace !important;
    font-size:.78rem !important; letter-spacing:.06em; border-radius:3px !important;
    padding:.45rem 1.1rem !important; transition:background .2s,box-shadow .2s;
}}
.stButton>button:hover {{background:var(--glow) !important; box-shadow:0 0 16px var(--glow);}}

[data-testid="stFileUploader"] {{
    background:var(--bg2) !important; border:1px dashed var(--muted) !important;
    border-radius:6px !important; padding:.6rem !important;
}}

[data-baseweb="tab-list"] {{background:var(--bg1) !important;border-bottom:1px solid var(--muted) !important;gap:0 !important;}}
[data-baseweb="tab"] {{
    font-family:'JetBrains Mono',monospace !important; font-size:.78rem !important;
    color:var(--text-dim) !important; background:transparent !important;
    border-bottom:2px solid transparent !important; padding:.6rem 1.4rem !important; letter-spacing:.05em;
}}
[aria-selected="true"][data-baseweb="tab"] {{color:var(--accent) !important;border-bottom:2px solid var(--accent) !important;background:transparent !important;}}

[data-testid="stExpander"] {{border:1px solid var(--muted) !important;border-radius:6px !important;background:var(--bg2) !important;}}
[data-testid="stExpander"] summary {{color:var(--accent2) !important;font-family:'JetBrains Mono',monospace !important;}}

[data-testid="stDataFrame"] {{border:1px solid var(--muted) !important;border-radius:6px !important;}}
.stDataFrame thead th {{background:var(--bg3) !important;color:var(--accent) !important;font-family:'JetBrains Mono',monospace !important;font-size:.72rem !important;}}

[data-baseweb="select"]>div {{background:var(--bg2) !important;border-color:var(--muted) !important;color:var(--text) !important;}}

textarea,.stTextArea textarea {{
    background:var(--bg2) !important; border:1px solid var(--muted) !important;
    color:var(--text) !important; font-family:'Space Grotesk',sans-serif !important;
    border-radius:6px !important;
}}
textarea:focus {{border-color:var(--accent) !important;outline:none !important;}}

[data-testid="stChatMessage"] {{
    background:var(--bg2) !important; border:1px solid var(--muted) !important;
    border-radius:8px !important; margin-bottom:.5rem !important;
}}
[data-testid="stChatMessage"] p {{font-family:'Space Grotesk',sans-serif !important;color:var(--text) !important;}}

hr {{border-color:var(--muted) !important;margin:1.4rem 0 !important;}}

.badge {{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.65rem;padding:.15rem .55rem;border-radius:2px;letter-spacing:.08em;text-transform:uppercase;}}
.badge-accent {{background:var(--glow);color:var(--accent);border:1px solid var(--accent2);}}
.badge-red    {{background:rgba(224,62,82,.12);color:var(--red);border:1px solid var(--red);}}
.badge-amber  {{background:rgba(217,119,6,.12);color:var(--amber);border:1px solid var(--amber);}}
.badge-cyan   {{background:rgba(2,132,199,.12);color:var(--cyan);border:1px solid var(--cyan);}}

.section-hdr {{
    font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--text-dim);
    text-transform:uppercase; letter-spacing:.14em; margin-bottom:.4rem;
    border-left:2px solid var(--accent); padding-left:.6rem;
}}
.glow-line {{height:1px;background:linear-gradient(90deg,var(--accent) 0%,transparent 100%);margin:1rem 0;opacity:.45;}}
.info-box {{
    background:var(--bg2); border:1px solid var(--muted); border-left:3px solid var(--accent);
    border-radius:0 6px 6px 0; padding:.9rem 1.2rem; margin:.6rem 0;
    font-family:'Space Grotesk',sans-serif; font-size:.88rem; color:var(--text); line-height:1.6;
}}
.info-box b {{color:var(--accent);font-weight:600;}}
</style>
""",unsafe_allow_html =True )

inject_css (T )




def acid_layout (fig ,title ="",height =380 ):
    fig .update_layout (
    title =dict (text =title ,font =dict (family ="Syne",size =14 ,color =T ["accent"]),x =0 ),
    paper_bgcolor =T ["plot_paper"],plot_bgcolor =T ["plot_bg"],
    font =dict (family ="Space Grotesk",color =T ["text"],size =12 ),
    height =height ,margin =dict (l =20 ,r =20 ,t =45 if title else 20 ,b =20 ),
    legend =dict (bgcolor ="rgba(0,0,0,0)",bordercolor =T ["muted"],borderwidth =1 ,
    font =dict (family ="JetBrains Mono",size =10 )),
    xaxis =dict (gridcolor =T ["grid"],zerolinecolor =T ["grid"],
    tickfont =dict (family ="JetBrains Mono",size =10 )),
    yaxis =dict (gridcolor =T ["grid"],zerolinecolor =T ["grid"],
    tickfont =dict (family ="JetBrains Mono",size =10 )),
    )
    return fig 




@st .cache_data (show_spinner =False )
def load_and_clean (raw_bytes :bytes )->pd .DataFrame :
    df =pd .read_csv (io .BytesIO (raw_bytes ))
    if "Item_Weight"in df .columns :df ["Item_Weight"]=df ["Item_Weight"].fillna (df ["Item_Weight"].mean ())
    if "Outlet_Size"in df .columns :df ["Outlet_Size"]=df ["Outlet_Size"].fillna (df ["Outlet_Size"].mode ()[0 ])
    if "Item_Visibility"in df .columns :
        med =df ["Item_Visibility"].replace (0 ,np .nan ).median ()
        df ["Item_Visibility"]=df ["Item_Visibility"].replace (0 ,med )
    if "Item_Fat_Content"in df .columns :
        df ["Item_Fat_Content"]=df ["Item_Fat_Content"].replace ({"low fat":"Low Fat","LF":"Low Fat","reg":"Regular"})
    if "Outlet_Establishment_Year"in df .columns :
        df ["Outlet_Age"]=2024 -df ["Outlet_Establishment_Year"]
    return df 

@st .cache_data (show_spinner =False )
def extract_pdf_text (raw_bytes :bytes )->str :
    try :
        import pdfplumber 
        with pdfplumber .open (io .BytesIO (raw_bytes ))as pdf :
            return "\n".join (p .extract_text ()or ""for p in pdf .pages )
    except Exception as e :
        return f"[PDF extraction error: {e }]"

@st .cache_data (show_spinner =False )
def train_model (df :pd .DataFrame ):
    from sklearn .linear_model import LinearRegression 
    from sklearn .ensemble import RandomForestRegressor 
    from sklearn .model_selection import train_test_split 
    from sklearn .metrics import r2_score ,mean_squared_error ,mean_absolute_error 

    target ="Item_Outlet_Sales"
    if target not in df .columns :return None 
    X =df .drop (columns =[c for c in ["Item_Identifier","Outlet_Identifier",target ]if c in df .columns ])
    y =df [target ]
    cats =X .select_dtypes (include ="object").columns .tolist ()
    if cats :X =pd .get_dummies (X ,columns =cats ,drop_first =False )
    X =X .fillna (X .mean (numeric_only =True ))
    Xtr ,Xte ,ytr ,yte =train_test_split (X ,y ,test_size =0.2 ,random_state =42 )
    lr =LinearRegression ().fit (Xtr ,ytr );lp =lr .predict (Xte )
    rf =RandomForestRegressor (120 ,random_state =42 ,n_jobs =-1 ).fit (Xtr ,ytr );rp =rf .predict (Xte )
    fi =pd .DataFrame ({"Feature":X .columns ,"Importance":rf .feature_importances_ }).sort_values ("Importance",ascending =False ).head (15 )
    cf =pd .DataFrame ({"Feature":X .columns ,"Coefficient":lr .coef_ })
    cf =cf .reindex (cf ["Coefficient"].abs ().sort_values (ascending =False ).index ).head (10 )
    return {
    "lr":lr ,"rf":rf ,"X_test":Xte ,"y_test":yte ,"lr_pred":lp ,"rf_pred":rp ,
    "lr_r2":r2_score (yte ,lp ),"rf_r2":r2_score (yte ,rp ),
    "lr_rmse":np .sqrt (mean_squared_error (yte ,lp )),"rf_rmse":np .sqrt (mean_squared_error (yte ,rp )),
    "lr_mae":mean_absolute_error (yte ,lp ),"rf_mae":mean_absolute_error (yte ,rp ),
    "feat_imp":fi ,"coef_df":cf ,"feature_names":list (X .columns ),
    }

def call_llm (system_prompt ,user_msg ,api_key ,provider ):
    try :
        if provider =="Groq (Free)":

            from groq import Groq 
            client =Groq (api_key =api_key )
            resp =client .chat .completions .create (
            model ="llama-3.3-70b-versatile",
            messages =[
            {"role":"system","content":system_prompt },
            {"role":"user","content":user_msg },
            ],
            max_tokens =1024 ,
            )
            return resp .choices [0 ].message .content 

        elif provider =="Gemini (Free)":

            import google .generativeai as genai 
            genai .configure (api_key =api_key )
            model =genai .GenerativeModel (
            model_name ="gemini-1.5-flash",
            system_instruction =system_prompt ,
            )
            resp =model .generate_content (user_msg )
            return resp .text 

        else :
            import anthropic 
            client =anthropic .Anthropic (api_key =api_key )
            msg =client .messages .create (
            model ="claude-sonnet-4-20250514",max_tokens =1024 ,
            system =system_prompt ,
            messages =[{"role":"user","content":user_msg }],
            )
            return msg .content [0 ].text 

    except ImportError as e :
        pkg =str (e ).split ("'")[1 ]if "'"in str (e )else str (e )
        return (f"Missing package — run:  pip install {pkg }\n\n"
        f"Full error: {e }")
    except Exception as e :
        return f"LLM error: {e }"




outlet_types ,fat_types ,mrp_range =[],[],None 

with st .sidebar :

    logo_svg =f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 58" width="170">
      <polygon points="29,5 53,17 53,41 29,53 5,41 5,17"
               fill="none" stroke="{T ['accent']}" stroke-width="2.5"/>
      <text x="29" y="34" text-anchor="middle" font-family="Arial Black,sans-serif"
            font-size="13" font-weight="900" fill="{T ['accent']}">MC</text>
      <text x="66" y="27" font-family="Arial Black,sans-serif" font-size="15"
            font-weight="900" fill="{T ['accent']}">MARKETCORP</text>
      <text x="66" y="41" font-family="Courier New,monospace" font-size="8"
            fill="{T ['text_dim']}" letter-spacing="2">ANALYTICS TERMINAL</text>
    </svg>"""
    st .markdown (logo_svg ,unsafe_allow_html =True )
    st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )


    st .markdown ('<p class="section-hdr">Theme</p>',unsafe_allow_html =True )
    choice =st .radio ("theme_radio",list (THEMES .keys ()),
    index =list (THEMES .keys ()).index (st .session_state .theme ),
    horizontal =True ,label_visibility ="collapsed")
    if choice !=st .session_state .theme :
        st .session_state .theme =choice 
        st .rerun ()

    st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )


    st .markdown ('<p class="section-hdr">01 · Data Import</p>',unsafe_allow_html =True )
    uploaded =st .file_uploader ("Drop CSV or PDF",type =["csv","pdf"],label_visibility ="collapsed")
    if uploaded :
        raw =uploaded .read ()
        if uploaded .name .endswith (".csv"):
            with st .spinner ("Ingesting and cleaning..."):
                st .session_state .df =load_and_clean (raw )
                st .session_state .ml_results =None 
            st .success (f"Loaded: {uploaded .name }")
            st .markdown (
            f'<span class="badge badge-accent">{st .session_state .df .shape [0 ]:,} rows</span> '
            f'<span class="badge badge-cyan">{st .session_state .df .shape [1 ]} cols</span>',
            unsafe_allow_html =True )
        else :
            with st .spinner ("Extracting PDF..."):
                st .session_state .pdf_text =extract_pdf_text (raw )
            st .success (f"Loaded: {uploaded .name }")


    st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )
    st .markdown ('<p class="section-hdr">02 · LLM Config</p>',unsafe_allow_html =True )

    provider =st .selectbox (
    "LLM Provider",
    ["Groq (Free)","Gemini (Free)","Anthropic (Paid)"],
    label_visibility ="collapsed",
    )

    PROVIDER_HELP ={
    "Groq (Free)":(
    "console.groq.com",
    "Sign up and create an API key."
    ),
    "Gemini (Free)":(
    "aistudio.google.com",
    "Sign in and get an API key."
    ),
    "Anthropic (Paid)":(
    "console.anthropic.com",
    "Requires credit card - pay per use."
    ),
    }
    url ,hint =PROVIDER_HELP [provider ]
    st .markdown (
    f'<p style="font-family:JetBrains Mono;font-size:.63rem;color:{T ["text_dim"]};line-height:1.75;">'
    f'<b style="color:{T ["accent"]};">{url }</b><br>{hint }</p>',
    unsafe_allow_html =True ,
    )
    placeholders ={"Groq (Free)":"gsk_...","Gemini (Free)":"AIza...","Anthropic (Paid)":"sk-ant-api03-..."}
    api_key =st .text_input ("API Key",type ="password",
    placeholder =placeholders [provider ],
    label_visibility ="collapsed")
    llm_ready =bool (api_key )
    st .markdown (
    f'<span class="badge {"badge-accent"if llm_ready else "badge-red"}">'
    f'{"LLM ACTIVE — "+provider if llm_ready else "NO KEY"}</span>',
    unsafe_allow_html =True ,
    )


    if st .session_state .df is not None :
        dfc =st .session_state .df 
        st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )
        st .markdown ('<p class="section-hdr">03 · Filters</p>',unsafe_allow_html =True )
        if "Outlet_Type"in dfc .columns :
            outlet_types =st .multiselect ("Outlet Type",sorted (dfc ["Outlet_Type"].unique ()),
            default =sorted (dfc ["Outlet_Type"].unique ()),
            label_visibility ="collapsed")
        if "Item_Fat_Content"in dfc .columns :
            fat_types =st .multiselect ("Fat Content",sorted (dfc ["Item_Fat_Content"].unique ()),
            default =sorted (dfc ["Item_Fat_Content"].unique ()),
            label_visibility ="collapsed")
        if "Item_MRP"in dfc .columns :
            mrp_range =st .slider ("Item MRP",float (dfc ["Item_MRP"].min ()),float (dfc ["Item_MRP"].max ()),
            (float (dfc ["Item_MRP"].min ()),float (dfc ["Item_MRP"].max ())))




def get_filtered_df ():
    if st .session_state .df is None :return None 
    df =st .session_state .df .copy ()
    try :
        if outlet_types and "Outlet_Type"in df .columns :df =df [df ["Outlet_Type"].isin (outlet_types )]
        if fat_types and "Item_Fat_Content"in df .columns :df =df [df ["Item_Fat_Content"].isin (fat_types )]
        if mrp_range and "Item_MRP"in df .columns :df =df [df ["Item_MRP"].between (*mrp_range )]
    except Exception :pass 
    return df 




theme_label ="ACID TERMINAL"if st .session_state .theme =="Acid Terminal"else "AZURE CLARITY"
st .markdown (f"""
<div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:.2rem;">
  <h1 style="margin:0;">MARKETCORP</h1>
  <span class="badge badge-accent">{theme_label } v2.0</span>
</div>
<p style="font-family:JetBrains Mono;font-size:.75rem;color:{T ['text_dim']};margin:0 0 1rem 0;">
  Retail Sales Intelligence &nbsp;·&nbsp; Data Pipeline &nbsp;·&nbsp; ML Forecasting &nbsp;·&nbsp; LLM Analyst
</p>
<div class="glow-line"></div>
""",unsafe_allow_html =True )




if st .session_state .df is None and not st .session_state .pdf_text :
    st .markdown (f"""
    <div style="text-align:center;padding:5rem 2rem;">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="72" style="margin-bottom:1.2rem;">
        <polygon points="40,6 72,22 72,58 40,74 8,58 8,22" fill="none" stroke="{T ['muted']}" stroke-width="3"/>
        <text x="40" y="46" text-anchor="middle" font-family="Arial Black,sans-serif"
              font-size="18" font-weight="900" fill="{T ['muted']}">MC</text>
      </svg>
      <h2 style="color:{T ['muted']};font-family:Syne;margin:.5rem 0;">AWAITING DATA SIGNAL</h2>
      <p style="color:{T ['text_dim']};font-family:JetBrains Mono;font-size:.78rem;line-height:1.8;">
        Upload a <span style="color:{T ['accent']};">CSV</span> for the full analytics pipeline<br>
        or a <span style="color:{T ['cyan']};">PDF</span> for document intelligence
      </p>
    </div>
    """,unsafe_allow_html =True )
    st .stop ()




tabs =st .tabs (["Overview","EDA","Deep Dive","ML Models","LLM Analyst"])




with tabs [0 ]:
    df =get_filtered_df ()
    if df is None :st .info ("Load a CSV.");st .stop ()

    has_target ="Item_Outlet_Sales"in df .columns 
    null_pct =df .isnull ().mean ().mean ()*100 

    c1 ,c2 ,c3 ,c4 ,c5 =st .columns (5 )
    with c1 :st .metric ("Total Records",f"{len (df ):,}")
    with c2 :st .metric ("Features",df .shape [1 ])
    with c3 :st .metric ("Avg Sales",f"${df ['Item_Outlet_Sales'].mean ():,.0f}"if has_target else "N/A")
    with c4 :st .metric ("Total Revenue",f"${df ['Item_Outlet_Sales'].sum ():,.0f}"if has_target else "N/A")
    with c5 :st .metric ("Data Completeness",f"{100 -null_pct :.1f}%")

    st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )

    cl ,cr =st .columns ([1.6 ,1 ])
    with cl :
        st .markdown ('<p class="section-hdr">Dataset Preview</p>',unsafe_allow_html =True )
        st .dataframe (df .head (20 ),use_container_width =True ,height =320 )
    with cr :
        st .markdown ('<p class="section-hdr">Column Audit</p>',unsafe_allow_html =True )
        audit =pd .DataFrame ({
        "Column":df .columns ,"Type":df .dtypes .astype (str ),
        "Nulls":df .isnull ().sum (),"Unique":df .nunique (),
        }).reset_index (drop =True )
        st .dataframe (audit ,use_container_width =True ,height =320 )

    st .markdown ('<p class="section-hdr">Numerical Summary</p>',unsafe_allow_html =True )
    st .dataframe (df .describe ().T .round (2 ),use_container_width =True )

    if df .isnull ().any ().any ():
        st .markdown ('<p class="section-hdr">Missing Value Map</p>',unsafe_allow_html =True )
        miss =(df .isnull ().mean ()*100 ).round (2 )
        miss =miss [miss >0 ].sort_values ()
        fig =go .Figure (go .Bar (x =miss .values ,y =miss .index ,orientation ="h",
        marker_color =T ["amber"],
        text =[f"{v :.1f}%"for v in miss .values ],
        textposition ="outside"))
        acid_layout (fig ,"Missing Values (%)",height =220 )
        st .plotly_chart (fig ,use_container_width =True )




with tabs [1 ]:
    df =get_filtered_df ()
    if df is None :st .info ("Load a CSV.");st .stop ()

    if "Item_Outlet_Sales"in df .columns :
        c1 ,c2 =st .columns (2 )
        with c1 :
            fig =go .Figure (go .Histogram (x =df ["Item_Outlet_Sales"],nbinsx =40 ,
            marker_color =T ["accent"],opacity =.85 ))
            acid_layout (fig ,"Distribution — Item Outlet Sales")
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            fig =go .Figure (go .Box (y =df ["Item_Outlet_Sales"],marker_color =T ["accent"],boxmean ="sd"))
            acid_layout (fig ,"Boxplot — Item Outlet Sales")
            st .plotly_chart (fig ,use_container_width =True )

    cat_cols =[c for c in ["Outlet_Type","Outlet_Size","Outlet_Location_Type","Item_Fat_Content"]if c in df .columns ]
    if cat_cols and "Item_Outlet_Sales"in df .columns :
        st .markdown ('<p class="section-hdr">Avg Sales by Category</p>',unsafe_allow_html =True )
        for row in [cat_cols [i :i +2 ]for i in range (0 ,len (cat_cols ),2 )]:
            cws =st .columns (len (row ))
            for cw ,cat in zip (cws ,row ):
                with cw :
                    grp =df .groupby (cat )["Item_Outlet_Sales"].mean ().sort_values (ascending =False ).reset_index ()
                    grp .columns =[cat ,"Avg_Sales"]
                    fig =px .bar (grp ,x =cat ,y ="Avg_Sales",color ="Avg_Sales",
                    color_continuous_scale =[[0 ,T ["grad_lo"]],[1 ,T ["grad_hi"]]],
                    text =grp ["Avg_Sales"].apply (lambda x :f"${x :,.0f}"))
                    fig .update_traces (textposition ="outside")
                    fig .update_layout (coloraxis_showscale =False ,xaxis_tickangle =-30 )
                    acid_layout (fig ,f"Avg Sales by {cat }")
                    st .plotly_chart (fig ,use_container_width =True )

    if "Item_MRP"in df .columns and "Item_Outlet_Sales"in df .columns :
        c1 ,c2 =st .columns ([1.6 ,1 ])
        with c1 :
            color_col ="Outlet_Type"if "Outlet_Type"in df .columns else None 
            samp =df .sample (min (1000 ,len (df )))
            fig =px .scatter (samp ,x ="Item_MRP",y ="Item_Outlet_Sales",
            color =color_col ,color_discrete_sequence =T ["palette"],opacity =.65 )
            xv ,yv =df ["Item_MRP"].values ,df ["Item_Outlet_Sales"].values 
            m ,b =np .polyfit (xv ,yv ,1 )
            xl =np .linspace (xv .min (),xv .max (),100 )
            fig .add_trace (go .Scatter (x =xl ,y =m *xl +b ,mode ="lines",
            line =dict (color =T ["accent"],width =2 ,dash ="dash"),name ="Trend"))
            acid_layout (fig ,"Item MRP vs Outlet Sales",height =400 )
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            if "Item_Type"in df .columns :
                grp2 =df .groupby ("Item_Type")["Item_Outlet_Sales"].mean ().sort_values ().reset_index ()
                fig =px .bar (grp2 ,x ="Item_Outlet_Sales",y ="Item_Type",orientation ="h",
                color ="Item_Outlet_Sales",
                color_continuous_scale =[[0 ,T ["grad_lo"]],[1 ,T ["grad_hi"]]])
                fig .update_layout (coloraxis_showscale =False )
                acid_layout (fig ,"Avg Sales by Item Type",height =400 )
                st .plotly_chart (fig ,use_container_width =True )

    pie_cols =[c for c in ["Outlet_Size","Item_Fat_Content","Outlet_Location_Type"]if c in df .columns ]
    if pie_cols :
        st .markdown ('<p class="section-hdr">Distribution Breakdown</p>',unsafe_allow_html =True )
        cws =st .columns (len (pie_cols ))
        for cw ,pc in zip (cws ,pie_cols ):
            with cw :
                vc =df [pc ].value_counts ().reset_index ();vc .columns =[pc ,"count"]
                fig =px .pie (vc ,names =pc ,values ="count",
                color_discrete_sequence =T ["palette"],hole =0.45 )
                fig .update_traces (textinfo ="label+percent",
                textfont =dict (family ="JetBrains Mono",size =10 ))
                acid_layout (fig ,pc ,height =280 )
                st .plotly_chart (fig ,use_container_width =True )




with tabs [2 ]:
    df =get_filtered_df ()
    if df is None :st .info ("Load a CSV.");st .stop ()

    num_cols =df .select_dtypes (include =np .number ).columns .tolist ()
    if len (num_cols )>=2 :
        st .markdown ('<p class="section-hdr">Correlation Matrix</p>',unsafe_allow_html =True )
        corr =df [num_cols ].corr ().round (2 )
        fig =go .Figure (go .Heatmap (
        z =corr .values ,x =corr .columns ,y =corr .columns ,
        colorscale =[[0 ,T ["bg3"]],[0.5 ,T ["muted"]],[1 ,T ["accent"]]],
        text =corr .values ,texttemplate ="%{text:.2f}",
        textfont =dict (family ="JetBrains Mono",size =10 ),showscale =True ,
        ))
        acid_layout (fig ,"Feature Correlation Heatmap",height =420 )
        st .plotly_chart (fig ,use_container_width =True )

    st .markdown ('<p class="section-hdr">GroupBy Drilldown</p>',unsafe_allow_html =True )
    cat_opts =df .select_dtypes (include ="object").columns .tolist ()
    if cat_opts and num_cols :
        c1 ,c2 ,c3 =st .columns (3 )
        with c1 :grp_by =st .selectbox ("Group by",cat_opts ,key ="grp_cat")
        with c2 :
            default ="Item_Outlet_Sales"if "Item_Outlet_Sales"in num_cols else num_cols [0 ]
            grp_val =st .selectbox ("Metric",num_cols ,key ="grp_num",index =num_cols .index (default ))
        with c3 :agg_fn =st .selectbox ("Aggregation",["mean","sum","median","count"],key ="grp_agg")
        gr =df .groupby (grp_by )[grp_val ].agg (agg_fn ).sort_values (ascending =False ).reset_index ()
        fig =px .bar (gr ,x =grp_by ,y =grp_val ,color =grp_val ,
        color_continuous_scale =[[0 ,T ["grad_lo"]],[1 ,T ["grad_hi"]]],
        text =gr [grp_val ].apply (lambda x :f"{x :,.1f}"))
        fig .update_traces (textposition ="outside")
        fig .update_layout (coloraxis_showscale =False ,xaxis_tickangle =-30 )
        acid_layout (fig ,f"{agg_fn .capitalize ()} of {grp_val } by {grp_by }",height =380 )
        st .plotly_chart (fig ,use_container_width =True )

    if "Outlet_Age"in df .columns and "Item_Outlet_Sales"in df .columns :
        st .markdown ('<p class="section-hdr">Outlet Age vs Sales</p>',unsafe_allow_html =True )
        c1 ,c2 =st .columns (2 )
        with c1 :
            fig =px .scatter (df .sample (min (800 ,len (df ))),x ="Outlet_Age",y ="Item_Outlet_Sales",
            color ="Outlet_Type"if "Outlet_Type"in df .columns else None ,
            color_discrete_sequence =T ["palette"],opacity =.65 )
            acid_layout (fig ,"Outlet Age vs Sales")
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            ab =pd .cut (df ["Outlet_Age"],bins =[0 ,10 ,20 ,30 ,40 ,50 ],
            labels =["<10yr","10-20yr","20-30yr","30-40yr","40+yr"])
            ag =df .groupby (ab ,observed =True )["Item_Outlet_Sales"].mean ().reset_index ()
            ag .columns =["Age_Group","Avg_Sales"]
            fig =px .bar (ag ,x ="Age_Group",y ="Avg_Sales",color ="Avg_Sales",
            color_continuous_scale =[[0 ,T ["grad_lo"]],[1 ,T ["grad_hi"]]],
            text =ag ["Avg_Sales"].apply (lambda x :f"${x :,.0f}"))
            fig .update_traces (textposition ="outside")
            fig .update_layout (coloraxis_showscale =False )
            acid_layout (fig ,"Avg Sales by Outlet Age Group")
            st .plotly_chart (fig ,use_container_width =True )

    if "Item_Identifier"in df .columns and "Item_Outlet_Sales"in df .columns :
        st .markdown ('<p class="section-hdr">Top and Bottom 15 Items</p>',unsafe_allow_html =True )
        c1 ,c2 =st .columns (2 )
        t15 =df .groupby ("Item_Identifier")["Item_Outlet_Sales"].sum ().nlargest (15 ).reset_index ()
        b15 =df .groupby ("Item_Identifier")["Item_Outlet_Sales"].sum ().nsmallest (15 ).reset_index ()
        with c1 :
            fig =px .bar (t15 ,x ="Item_Outlet_Sales",y ="Item_Identifier",orientation ="h",
            color ="Item_Outlet_Sales",
            color_continuous_scale =[[0 ,T ["grad_lo"]],[1 ,T ["grad_hi"]]])
            fig .update_layout (coloraxis_showscale =False )
            acid_layout (fig ,"Top 15 Items by Total Sales",height =380 )
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            fig =px .bar (b15 ,x ="Item_Outlet_Sales",y ="Item_Identifier",orientation ="h",
            color ="Item_Outlet_Sales",
            color_continuous_scale =[[0 ,T ["accent"]],[1 ,T ["red"]]])
            fig .update_layout (coloraxis_showscale =False )
            acid_layout (fig ,"Bottom 15 Items by Total Sales",height =380 )
            st .plotly_chart (fig ,use_container_width =True )




with tabs [3 ]:
    df =get_filtered_df ()
    if df is None or "Item_Outlet_Sales"not in df .columns :
        st .info ("Load a CSV with an Item_Outlet_Sales column.");st .stop ()

    if st .button ("Train Models",key ="train_btn"):
        with st .spinner ("Training Linear Regression and Random Forest..."):
            st .session_state .ml_results =train_model (df )
        st .success ("Models trained.")

    ml =st .session_state .ml_results 
    if ml is None :
        st .markdown ('<div class="info-box">Hit <b>Train Models</b> to run the full ML pipeline — '
        'Linear Regression and Random Forest on a 80/20 split, with feature importances, '
        'coefficients, and residual diagnostics.</div>',unsafe_allow_html =True )
    else :
        st .markdown ('<p class="section-hdr">Model Scorecard</p>',unsafe_allow_html =True )
        c1 ,c2 ,c3 ,c4 ,c5 ,c6 =st .columns (6 )
        with c1 :st .metric ("LR  R2",f"{ml ['lr_r2']:.3f}")
        with c2 :st .metric ("LR  RMSE",f"{ml ['lr_rmse']:,.0f}")
        with c3 :st .metric ("LR  MAE",f"{ml ['lr_mae']:,.0f}")
        with c4 :st .metric ("RF  R2",f"{ml ['rf_r2']:.3f}")
        with c5 :st .metric ("RF  RMSE",f"{ml ['rf_rmse']:,.0f}")
        with c6 :st .metric ("RF  MAE",f"{ml ['rf_mae']:,.0f}")
        st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )

        yte =ml ["y_test"];rng =[float (yte .min ()),float (yte .max ())]
        c1 ,c2 =st .columns (2 )
        with c1 :
            fig =go .Figure ([
            go .Scatter (x =yte ,y =ml ["lr_pred"],mode ="markers",
            marker =dict (color =T ["cyan"],opacity =.5 ,size =5 ),name ="Predicted"),
            go .Scatter (x =rng ,y =rng ,mode ="lines",
            line =dict (color =T ["accent"],dash ="dash",width =1.5 ),name ="Perfect Fit"),
            ])
            acid_layout (fig ,"LR — Actual vs Predicted")
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            fig =go .Figure ([
            go .Scatter (x =yte ,y =ml ["rf_pred"],mode ="markers",
            marker =dict (color =T ["amber"],opacity =.5 ,size =5 ),name ="Predicted"),
            go .Scatter (x =rng ,y =rng ,mode ="lines",
            line =dict (color =T ["accent"],dash ="dash",width =1.5 ),name ="Perfect Fit"),
            ])
            acid_layout (fig ,"RF — Actual vs Predicted")
            st .plotly_chart (fig ,use_container_width =True )

        c1 ,c2 =st .columns (2 )
        with c1 :
            fig =go .Figure (go .Histogram (x =yte .values -ml ["lr_pred"],nbinsx =40 ,
            marker_color =T ["cyan"],opacity =.85 ))
            acid_layout (fig ,"LR Residuals Distribution")
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            fig =go .Figure (go .Histogram (x =yte .values -ml ["rf_pred"],nbinsx =40 ,
            marker_color =T ["amber"],opacity =.85 ))
            acid_layout (fig ,"RF Residuals Distribution")
            st .plotly_chart (fig ,use_container_width =True )

        c1 ,c2 =st .columns (2 )
        with c1 :
            fi =ml ["feat_imp"]
            fig =px .bar (fi ,x ="Importance",y ="Feature",orientation ="h",color ="Importance",
            color_continuous_scale =[[0 ,T ["grad_lo"]],[1 ,T ["grad_hi"]]])
            fig .update_layout (coloraxis_showscale =False ,yaxis =dict (autorange ="reversed"))
            acid_layout (fig ,"RF — Top 15 Feature Importances",height =420 )
            st .plotly_chart (fig ,use_container_width =True )
        with c2 :
            cf =ml ["coef_df"].copy ()
            clr =[T ["accent"]if v >0 else T ["red"]for v in cf ["Coefficient"]]
            fig =go .Figure (go .Bar (x =cf ["Coefficient"],y =cf ["Feature"],
            orientation ="h",marker_color =clr ))
            acid_layout (fig ,"LR — Top 10 Coefficients",height =420 )
            st .plotly_chart (fig ,use_container_width =True )

        st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )
        st .markdown ('<p class="section-hdr">Live Sales Predictor (RF)</p>',unsafe_allow_html =True )
        pc1 ,pc2 ,pc3 ,pc4 =st .columns (4 )
        with pc1 :pm =st .number_input ("Item MRP",10. ,300. ,150. ,1. )
        with pc2 :pw =st .number_input ("Item Weight kg",1. ,25. ,13. ,.1 )
        with pc3 :pv =st .number_input ("Item Visibility",0. ,.4 ,.09 ,.01 )
        with pc4 :pa =st .number_input ("Outlet Age yrs",1 ,40 ,15 ,1 )
        if st .button ("Predict Sales",key ="pred_btn"):
            fn =ml ["feature_names"]
            Xp =pd .DataFrame ([{f :0 for f in fn }])
            for col ,val in [("Item_MRP",pm ),("Item_Weight",pw ),("Item_Visibility",pv ),("Outlet_Age",pa )]:
                if col in Xp .columns :Xp [col ]=val 
            pred =ml ["rf"].predict (Xp )[0 ]
            st .markdown (
            f'<div class="info-box">Predicted <b>Item Outlet Sales</b>: '
            f'<span style="font-size:1.6rem;font-family:Syne;color:{T ["accent"]};">'
            f'${pred :,.2f}</span></div>',unsafe_allow_html =True )




with tabs [4 ]:
    st .markdown ('<p class="section-hdr">AI Data Analyst</p>',unsafe_allow_html =True )

    if not llm_ready :
        st .markdown ('<div class="info-box">Enter your <b>Anthropic API key</b> in the sidebar to activate the LLM analyst.</div>',
        unsafe_allow_html =True )
        st .stop ()

    ctx =[]
    if st .session_state .df is not None :
        dfc =get_filtered_df ()
        ctx .append (f"=== DATASET ===\nShape: {dfc .shape }\nColumns: {list (dfc .columns )}\n"
        f"Stats:\n{dfc .describe ().round (2 ).to_string ()}\n"
        f"Nulls:\n{dfc .isnull ().sum ().to_string ()}\n"
        f"Sample:\n{dfc .head (5 ).to_string ()}")
    if st .session_state .ml_results :
        ml =st .session_state .ml_results 
        ctx .append (f"=== ML RESULTS ===\n"
        f"LR: R2={ml ['lr_r2']:.3f} RMSE={ml ['lr_rmse']:,.0f} MAE={ml ['lr_mae']:,.0f}\n"
        f"RF: R2={ml ['rf_r2']:.3f} RMSE={ml ['rf_rmse']:,.0f} MAE={ml ['rf_mae']:,.0f}\n"
        f"Feature Importance:\n{ml ['feat_imp'].to_string ()}\n"
        f"LR Coefficients:\n{ml ['coef_df'].to_string ()}")
    if st .session_state .pdf_text :
        ctx .append (f"=== PDF CONTENT ===\n{st .session_state .pdf_text [:4000 ]}")

    SYSTEM =("You are an elite retail analytics AI embedded in MarketCorp Analytics Terminal. "
    "You have deep expertise in sales analytics, ML interpretation, and business strategy. "
    "Be sharp, professional, and grounded in the data provided.\n\n"
    +("\n\n".join (ctx )if ctx else "No data loaded."))

    st .markdown ('<p class="section-hdr">Quick Insights</p>',unsafe_allow_html =True )
    presets ={
    "Sales Summary":"Summarise key sales performance insights in 3-5 sharp points.",
    "Outlet Analysis":"Which outlet types and sizes drive the highest sales and why? Give recommendations.",
    "Model Insights":"Interpret the ML model results. Which features matter most? What does R2 tell us?",
    "Recommendations":"Give 5 concrete strategic recommendations to grow MarketCorp revenue.",
    }
    cws =st .columns (4 )
    for cw ,(label ,prompt )in zip (cws ,presets .items ()):
        with cw :
            if st .button (label ,key =f"p_{label }"):
                st .session_state .chat_history .append ({"role":"user","content":prompt })
                with st .spinner ("Analysing..."):
                    st .session_state .chat_history .append ({"role":"assistant","content":call_llm (SYSTEM ,prompt ,api_key ,provider )})

    st .markdown ('<div class="glow-line"></div>',unsafe_allow_html =True )

    for msg in st .session_state .chat_history :
        with st .chat_message (msg ["role"]):
            st .markdown (msg ["content"])

    if prompt :=st .chat_input ("Ask anything about the data, models, or uploaded PDF..."):
        st .session_state .chat_history .append ({"role":"user","content":prompt })
        with st .chat_message ("user"):st .markdown (prompt )
        with st .chat_message ("assistant"):
            with st .spinner ("Thinking..."):
                reply =call_llm (SYSTEM ,prompt ,api_key ,provider )
            st .markdown (reply )
        st .session_state .chat_history .append ({"role":"assistant","content":reply })

    if st .session_state .chat_history :
        if st .button ("Clear conversation",key ="clr"):
            st .session_state .chat_history =[]
            st .rerun ()