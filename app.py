import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Retention Intelligence", page_icon="📺", layout="wide")

@st.cache_data
def load_data():
    df=pd.read_csv("data.csv")
    df["Retention"]=df["Retained_Flag"].map({1:"Retained",0:"Churned"})
    return df

df=load_data()
st.title("📺 Streaming Retention Intelligence")
st.caption("Viewer engagement patterns associated with subscriber retention")

with st.sidebar:
    st.header("Filters")
    genres=st.multiselect("Genre",sorted(df.Genre.unique()),default=sorted(df.Genre.unique()))
    available=sorted(df[df.Genre.isin(genres)].Title.unique())
    titles=st.multiselect("Content",available,default=available)
    filtered=df[df.Genre.isin(genres)&df.Title.isin(titles)]
    st.divider()
    st.caption("Demo dataset. Association does not imply causation.")

if filtered.empty:
    st.warning("No records match the selected filters."); st.stop()

c1,c2,c3,c4=st.columns(4)
c1.metric("Records",f"{len(filtered):,}")
c2.metric("Retention Rate",f"{filtered.Retained_Flag.mean()*100:.1f}%")
c3.metric("Avg Watch Duration",f"{filtered.Watch_Duration_Min.mean():.1f} min")
c4.metric("Avg Completion",f"{filtered.Completion_Pct.mean():.1f}%")

a,b=st.columns(2)
with a:
    x=filtered.groupby("Retention",as_index=False).Completion_Pct.mean()
    st.plotly_chart(px.bar(x,x="Retention",y="Completion_Pct",title="Completion by Retention",
                           labels={"Completion_Pct":"Completion (%)","Retention":""}),use_container_width=True)
with b:
    x=filtered.groupby("Retention",as_index=False).Watch_Duration_Min.mean()
    st.plotly_chart(px.bar(x,x="Retention",y="Watch_Duration_Min",title="Watch Duration by Retention",
                           labels={"Watch_Duration_Min":"Minutes","Retention":""}),use_container_width=True)

a,b=st.columns(2)
with a:
    x=filtered.groupby("Genre",as_index=False).Retained_Flag.mean()
    x["Retained_Flag"]*=100
    st.plotly_chart(px.bar(x.sort_values("Retained_Flag",ascending=False),x="Genre",y="Retained_Flag",
                           title="Retention by Genre",labels={"Retained_Flag":"Retention (%)"}),use_container_width=True)
with b:
    x=filtered.groupby(["Movie_ID","Title"],as_index=False).Retained_Flag.mean()
    x["Retained_Flag"]*=100
    x=x.sort_values("Retained_Flag",ascending=False).head(10)
    st.plotly_chart(px.bar(x.sort_values("Retained_Flag"),x="Retained_Flag",y="Title",orientation="h",
                           title="Top Content by Retention",labels={"Retained_Flag":"Retention (%)","Title":""}),use_container_width=True)

st.plotly_chart(px.scatter(filtered,x="Completion_Pct",y="Watch_Duration_Min",color="Retention",
                           hover_data=["Title","Genre"],title="Completion vs Watch Duration",
                           labels={"Completion_Pct":"Completion (%)","Watch_Duration_Min":"Watch duration (min)"}),use_container_width=True)

st.subheader("Key Insights")
r=filtered[filtered.Retained_Flag==1]; c=filtered[filtered.Retained_Flag==0]
if len(r) and len(c):
    st.write(f"• Retained records differ by {r.Completion_Pct.mean()-c.Completion_Pct.mean():+.1f} percentage points in average completion.")
    st.write(f"• Retained records differ by {r.Watch_Duration_Min.mean()-c.Watch_Duration_Min.mean():+.1f} minutes in average watch duration.")
    st.write(f"• Retained records differ by {r.Pause_Count.mean()-c.Pause_Count.mean():+.1f} pauses/view in average pause frequency.")
st.info("These results show associations in the available data; they do not establish causation.")
