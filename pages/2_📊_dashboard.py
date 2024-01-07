from pathlib import Path
import pandas as pd
pd.set_option('io.excel.xlsx.writer', 'openpyxl')
import streamlit as st
import utils as ut
import plotly.express as px
import numpy as np
from prophet import Prophet
import pmdarima
from statsmodels.tsa.arima.model import ARIMA
import datetime as dt
import plotly
import plotly.graph_objs as go
from static.templateEngine import write
import streamlit_authenticator as stauth
import json

st.set_page_config(layout='wide')


if 'authentication_status' in st.session_state:
    if st.session_state['authentication_status']:
        with st.expander("Format dokumen"):
            st.markdown('''
            - Format dokumen yang digunakan adalah excel
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

                subtab_overview, subtab_table, subtab_prediksi, subtab_report = st.tabs(['Overview', 'Tabel', 'Prediksi', 'Report'])

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
                with subtab_table:
                    st.subheader("Tabel", divider="blue")
                    # select tahun
                    listTahun = ut.getYear(dataframe)
                    year_select = st.selectbox("Pilih tahun", listTahun, help='Filter data berdasarkan tahun', key='st1')
                    # select bulan
                    listBulan = ut.getMonthFromYear(dataframe,year_select)
                    month_select = st.selectbox("Pilih bulan", listBulan, help='Filter data berdasarkan bulan', key='st2')
                    # select kolom
                    values = ut.getColumnName(dataframe, '-')
                    options = st.selectbox(
                        'Pilih kolom yang akan digunakan',
                        options= values,
                        key='select_data_tabel',
                        help="Pilih data yang akan digunakan untuk analisa tabel dan prediksi"
                    )
                    if (options == "-"):
                        st.info("Pilih kolom data terlebih dahulu")
                    set_point = st.number_input(label='Masukkan nilai set point', min_value=0)

                    clicked = st.button(label='Submit', key='btn1')

                    if clicked and options != '-':
                        with st.spinner('Menerapkan nilai set point...'):
                            filteredData = ut.filteredData(dataframe, year_select, month_select)
                            filtered = pd.DataFrame(filteredData[options])
                            c1, c2 = st.columns((2.5,7.5))
                            if set_point > 0:
                                filteredFormatted = np.round(filtered, decimals=2)
                                data = filteredFormatted.style.map(lambda x: ut._color_red_or_green(x, set_point)).format(precision=2, thousands=".", decimal=",") 
                                # data = filtered.style.map(lambda x: ut._color_red_or_green(x, set_point))  
                                c1.dataframe(data)
                            else:
                                c1.dataframe(filtered)
                            fig = px.line(filtered, x=filtered.index, y=options, markers=True, title=f'Nilai {options} pada bulan {month_select} tahun {year_select}')
                            fig.update_layout(
                                    xaxis_title='Date', 
                                    yaxis_title='Value')
                            fig.update_xaxes(
                                    dtick="86400000"
                            )
                            fig.update_traces(textfont_size=14)
                            series = filtered.copy()
                            series = series[options].apply(lambda x: float(f"{x: .2f}"))
                            series = series.squeeze()
                            filtered2 = series.to_frame(name=options)
                            fig.add_bar(x=filtered.index, y=filtered2[options], text=filtered2[options], name=options) 
                            # fig.add_vrect(annotation_textangle=90)
                            fig.add_hline(y=set_point, line_width=3, line_dash="dash", line_color="red")
                            c2.plotly_chart(fig, use_container_width=True)
                    elif clicked and options == '-':
                        st.warning('Pilih kolom data yang akan digunakan')
                    else:
                        st.info('Klik tombol submit untuk menerapkan nilai set point')
                with subtab_prediksi:
                    st.subheader("Hasil Prediksi 30 hari kedepan")
                    values = ut.getColumnName(dataframe, '-')
                    options = st.selectbox(
                        'Pilih kolom yang akan digunakan',
                        options= values,
                        key='select_data_prediksi',
                        help="Pilih data yang akan digunakan untuk analisa tabel dan prediksi"
                    )
                    selectModel = st.selectbox(label="Pilih model algoritma prediksi", options=["-","Prophet", "Auto ARIMA", "ARIMA"])
                    set_point = st.number_input(label='Masukkan nilai set point', min_value=0, key="set_point_predict")
                    clicked = st.button(label='Submit', key='btn2')
                    if clicked:
                        with st.spinner('Membuat prediksi...'):
                            if options == "-":
                                st.warning("Pilih kolom data yang akan digunakan")
                            if selectModel == "-":
                                st.warning("pilih model algoritma yang akan digunakan")
                            elif selectModel == "Prophet":
                                data = dataframe.copy()
                                
                                # data.columns.values[0] = "Tanggal"
                                data['Tanggal'] = data['Tanggal'].apply(lambda x: x.strftime('%Y-%m-%d'))
                                
                                data = data.set_index('Tanggal')
                                data = data[options]
                                data = data.reset_index()
                                data.columns = ['ds', 'y']
                                data['ds']= np.array(pd.to_datetime(data['ds']))
                                

                                model = Prophet()
                                # fit the model
                                model.fit(data)

                                # initializing date
                                start_date = dt.datetime.strptime(f"{data['ds'].iloc[-1]}", "%Y-%m-%d %H:%M:%S")
                                
                                # initializing K
                                K = 30
                                
                                future = pd.date_range(start_date, periods=K)
                                future = pd.DataFrame(future)
                                future.columns = ['ds']
                                future['ds']= np.array(pd.to_datetime(future['ds']))

                                #Predict 
                                forecast = model.predict(future)
                                forecast = forecast[["ds","yhat"]]
                                forecast = pd.DataFrame(forecast)
                                forecast.columns = ["date", options]
                                forecast = forecast.set_index("date")
                                
                                c1, c2 = st.columns((2.5,7.5))
                                if set_point > 0:
                                    filteredFormatted = np.round(forecast, decimals=2)
                                    data = filteredFormatted.style.map(lambda x: ut._color_red_or_green(x, set_point)).format(precision=2, thousands=".", decimal=",") 
                                    # data = filtered.style.map(lambda x: ut._color_red_or_green(x, set_point))  
                                    c1.dataframe(data)
                                else:
                                    c1.dataframe(forecast)
                                fig = px.line(forecast, x=forecast.index, y=options, markers=True, title=f'Prediksi nilai {options} 30 hari kedepan')
                                fig.update_layout(
                                        xaxis_title='Date', 
                                        yaxis_title='Value')
                                fig.update_xaxes(
                                        dtick="86400000"
                                )
                                fig.update_traces(textfont_size=14)
                                series = forecast.copy()
                                series = series[options].apply(lambda x: float(f"{x: .2f}"))
                                series = series.squeeze()
                                filtered2 = series.to_frame(name=options)
                                fig.add_bar(x=forecast.index, y=filtered2[options], text=filtered2[options], name=options) 
                                fig.add_hline(y=set_point, line_width=3, line_dash="dash", line_color="red")
                                c2.plotly_chart(fig, use_container_width=True)
                            elif selectModel == "Auto ARIMA":
                                data = dataframe.copy()
                                data = data.set_index('Tanggal')
                                data = data[options]
                                arima = pmdarima.auto_arima(data, 
                                m=7, 
                                # information_criterion="aicc", 
                                suppress_warnings=True,
                                trace=True,
                                d=None, 
                                test='adf',
                                start_p=0, start_q=0,
                                max_p=12, max_q=12)

                                n_forecast = 30
                                pred = arima.predict(n_forecast)
                                # dates = pd.date_range(test.index[0], periods=n_forecast, freq="D")
                                dates = pd.date_range(data.index[-1], periods=n_forecast, freq="D")
                                pred = pd.DataFrame({
                                    "Tanggal": dates,
                                    "value": pred
                                })
                                pred = pred.set_index("Tanggal")
                                c1, c2 = st.columns((2.5,7.5))
                                if set_point > 0:
                                    filteredFormatted = np.round(pred, decimals=2)
                                    data = filteredFormatted.style.map(lambda x: ut._color_red_or_green(x, set_point)).format(precision=2, thousands=".", decimal=",") 
                                    # data = filtered.style.map(lambda x: ut._color_red_or_green(x, set_point))  
                                    c1.dataframe(data)
                                else:
                                    c1.dataframe(pred)
                                fig = px.line(pred, x=pred.index, y="value", markers=True, title=f'Prediksi nilai {options} 30 hari kedepan')
                                fig.update_layout(
                                        xaxis_title='Date', 
                                        yaxis_title='Value')
                                fig.update_xaxes(
                                        dtick="86400000"
                                )
                                fig.update_traces(textfont_size=14)
                                series = pred.copy()
                                series = series["value"].apply(lambda x: float(f"{x: .2f}"))
                                series = series.squeeze()
                                filtered2 = series.to_frame(name="value")
                                fig.add_bar(x=pred.index, y=filtered2["value"], text=filtered2["value"], name="value") 
                                fig.add_hline(y=set_point, line_width=3, line_dash="dash", line_color="red")
                                c2.plotly_chart(fig, use_container_width=True)
                            elif selectModel == "ARIMA":
                                st.write("arima")
                    else:
                        st.info('Klik submit untuk memprediksi data')
                with subtab_report:
                    st.subheader("Report", divider="blue")
                    listTahun = ut.getYear(dataframe)
                    year_select = st.selectbox("Pilih tahun", listTahun, help='Filter data berdasarkan tahun', key='reportst1')

                    listBulan = ut.getMonthFromYear(dataframe,year_select)
                    month_select = st.selectbox("Pilih bulan", listBulan, help='Filter data berdasarkan bulan', key='reportst2')

                    listTanggal = ut.getDayFromMonth(dataframe,year_select,month_select)
                    day_select = st.selectbox("Pilih tanggal", listTanggal, help='Filter data berdasarkan tanggal', key='reportst3')

                    clicked = st.button(label='Create Report', key='btn3')

                    if clicked:
                        st.spinner("Processing your report")
                        write()
                        st.download_button(
                            "Download template", Path("./tabel_report.html").read_bytes(), "tabel_report.html"
                        )

            except Exception as e:
                st.error(e)
                st.error("Ada masalah saat membaca file excel, gunakan format sesuai template dan pastikan format dokumen sesuai dengan panduan.")
    elif st.session_state['authentication_status'] == None:
        st.warning("Diharapkan untuk login terlebih dahulu")
    else:
        st.error('Terjadi kesalahan pada aplikasi')
else:
    st.warning("Diharapkan untuk login terlebih dahulu")