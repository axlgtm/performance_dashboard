from pathlib import Path
import pandas as pd
pd.set_option('io.excel.xlsx.writer', 'openpyxl')
import streamlit as st
import utils as ut
import plotly.express as px

# st.write(Path("./static/template.xlsx").read_bytes())

st.set_page_config(layout='wide')

with st.expander("Format dokumen"):
    st.markdown('''
    - Format dokumen yang digunakan adalahexcel
    - Nilai kosong diisi oleh angka nol (Karena akan mengganggu aplikasi saat melakukan penghitungan)
    - Format tanggal **dd/mm/yyyy** 
    > contoh: 1 Agustus 2023 akan menjadi 1/8/2023
    **Notes :** Gunakan template yang telah disediakan untuk menghindari error pada aplikasi
    ''')
    st.download_button(
        "Download template", Path("./static/template.xlsx").read_bytes(), "template.xlsx"
    )

uploaded_file = st.file_uploader("Choose a file", type=['xls', 'xlsx'])

if uploaded_file is not None:
    try:
        fileName = uploaded_file.name.split('.')
        # check if file format didnt excel
        if fileName[1] != "xlsx" and fileName[1] != "xls":
            st.error("Format file tidak sesuai")
        
        # read file
        dataframe = pd.read_excel(uploaded_file)
        # st.table(dataframe.dtypes) 
        # st.table(ut.normalizeDataframe(dataframe))
        dataframe.set_index('Tanggal')

        ## ---- generate kolom by excel ------
        try:
            dataframe = ut.generateColumn(dataframe)
        except Exception as e:
            st.error(e)
            st.error("Generate kolom gagal, pastikan nama kolom sesuai dengan format template")
        ## ---- end generate kolom by excel ------

        subtab_overview, subtab_table = st.tabs(['Overview', 'Prediksi'])

        with subtab_overview:
            st.subheader("Quick Metrics",divider="blue")
            selectKolMet = st.selectbox(label="Pilih kolom", options=["-","Finish Goods","Water (M3/TON)", 'Energy (KWH/TON)'])
            c1, c2 = st.columns(2)
            c1.markdown(f'##### Nilai total {selectKolMet}')
            c2.markdown(f'##### Nilai rata-rata {selectKolMet}')

            s1, s2 = c1.columns(2)
            t1, t2 = c2.columns(2)

            st.subheader("Menu Utama", divider="blue")
            # st.write(ut.getColumnName(dataframe))
            values = ut.getColumnName(dataframe)
            options = st.multiselect(
                'Pilih kolom',
                options= values,
                key='select_data',
                help="Dapat memilih lebih dari 1 data",
                default= values[0]
            )
            # st.write("Pilih tahun dan bulan")
            if len(options) == 0:
                st.info("Pilih kolom data terlebih dahulu")
            # st.dataframe(ut.getYear(dataframe))
            listTahun = ut.getYear(dataframe)
            year_select = st.selectbox("Pilih tahun", listTahun, help='Filter data berdasarkan tahun')

            listBulan = ut.getMonthFromYear(dataframe,year_select)
            month_select = st.selectbox("Pilih bulan", listBulan, help='Filter data berdasarkan bulan')

            filteredDataframe = ut.filteredData(dataframe, year_select, ut.decodeMonth(month_select))

            st.divider()
            st.markdown(f'##### Grafik Parameter Harian')
            st.info("Section data parameter harian dalam satu bulan")
            c1, c2 = st.columns(2)

            with c1:
                fig = ut.barChart(filteredDataframe, options)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = ut.lineChart(filteredDataframe, options)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f'##### Grafik Total Data Nilai Parameter Bulanan')
            st.info("Section total data parameter dalam satu bulan")

            monthData = ut.sumByMonth(dataframe, year_select)
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(ut.barChartMonthlyData(monthData, options))
            with c2:
                st.plotly_chart(ut.lineChartMonthlyData(monthData, options))
            

            st.markdown("#### Grafik Prosentase Perubahan Nilai Total Parameter Bulanan")
            st.info("Section prosentase perubahan total data parameter tiap bulan dalam satu tahun")

            monthPercentage = ut.percentageMonthly(monthData)
            fig = px.line(monthPercentage, x=monthPercentage.index, y=options, color_discrete_sequence=px.colors.qualitative.Pastel, markers=True)
            
            fig.update_layout(
                xaxis_title='Month', 
                yaxis_title='Percentage Change (%)')
            fig.update_xaxes(
                dtick="M1",
                tick0=""
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### Grafik Total Data Nilai Parameter Tahunan")
            st.info("Section total data parameter dalam satu tahun")

            yearData = ut.sumOfYear(dataframe, options)
            # st.dataframe(yearData)
            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(yearData, x=yearData.index, y=options, color_discrete_sequence=px.colors.qualitative.Pastel, barmode='group', text_auto=True)
                fig.update_layout(
                        xaxis_title='Year', 
                        yaxis_title='Value')
                fig.update_xaxes(
                    dtick="M12"
                )
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = px.line(yearData, x=yearData.index, y=options, color_discrete_sequence=px.colors.qualitative.Pastel, markers=True)
        
                fig.update_layout(
                    xaxis_title='Year', 
                    yaxis_title='Value')
                fig.update_xaxes(
                    dtick="M12",
                    tick0=""
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(e)
        st.error("Ada masalah saat membaca file excel, gunakan format sesuai template dan pastikan format dokumen sesuai dengan panduan.")