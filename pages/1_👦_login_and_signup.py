import streamlit as st
import streamlit_authenticator as stauth
import utils as ut
from pathlib import Path

st.set_page_config(page_title="Login and Signup Page")

# menggunakan yaml config
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

try:
    st.subheader("Login and Signup Page", divider=True)
    pageMenu = st.selectbox("Pilih Menu", ["Login", "Signup"])
    authentication_status = False # ditambahkan agar line 109 tdk error
    username = None
    if pageMenu == "Login":
        name, authentication_status, username = authenticator.login("login", "main")
        if authentication_status:
            st.info(f'Selamat datang :blue[{name}]')
            st.session_state['authentication_status'] = True
            authenticator.logout('Logout', 'main', key='abcde')
        if authentication_status is False:
            st.error('Username/password is incorrect')
        elif authentication_status is None:
            st.warning('Please enter your username and password')
    elif pageMenu == "Signup":
        try :
            if authenticator.register_user('Register user', preauthorization=True):
                st.success('User registered successfully')
                st.balloons()
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(f'Ada masalah saat menambahkan user, pesan: {e}')
#  ----------------------- Admin Previelege -----------------------------
    if authentication_status and username == "admin": 
        st.header(":green[Administrator] Menu", divider=True)
        st.info("Hanya admin yang dapat melihat menu dibawah")
# ---------------- Akun terdaftar menu -------------------
        st.subheader("Akun yang terdaftar", divider=True)
        with open('config.yaml', 'r') as f:
            data = yaml.safe_load(f)
            rerult = data['credentials']['usernames']
            usernames = list(rerult.keys())
            names = []
            email = []
            # st.write(rerult['admin'])
            # st.write(usernames)
            for item in usernames:
                data = rerult[item]
                names.append(data['name'])
                email.append(data['email'])
            c1, c2 = st.columns(2)
            c1.dataframe({
                "usernames": usernames,
                "names": names,
                "email": email
            })
            c2.download_button(
                "Download arsip akun terdaftar", Path("config.yaml").read_bytes(), "arsip_akun_terdaftar.yaml"
            )
# ---------------- Menambahkan predefined Akun -----------------------
        st.subheader("Predefined User", divider=True)
        st.info("Predefined User adalah akun email yang telah diijinkan untuk melakukan registrasi oleh admin")
        with st.form("predefined_form"):
            predefinedEmailInput = st.text_input("Masukkan email yang akan diijinkan registrasi user")
            submitted = st.form_submit_button("Add predefined user")
            if submitted:
                try:
                    listedEmail = ut.read_emails()
                    listedEmail.append(predefinedEmailInput)
                    st.write(listedEmail)
                    with open('config.yaml') as f:
                        doc = yaml.load(f, Loader=SafeLoader)
                    doc['preauthorized']['emails'] = listedEmail
                    with open('config.yaml', 'w') as f:
                        yaml.dump(doc, f, default_flow_style=False)
                    st.success('Berhasil menambahkan predefined user')
                except Exception as e:
                    st.error(f'Predefined user gagal dibuat, pesan: {e}')
except Exception as e:
    st.error(f'Ada masalah pada aplikasi, pesan: {e}')


# ------------- pembatas dgn login sqlite -------

# try:
#     # persiapan data db sqlite3
#     engine = create_engine("sqlite:///db.sqlite3")
#     Session = sessionmaker(engine)
#     session = Session()

#     try:
#         query = session.query(user).all()
#         queryPredefined = session.query(predefinedUser).all()
#         predefinedEmail = []
#         names = []
#         usernames = []
#         passwords = []
#         emails = []
#         cred = {
#             "usernames": {

#             }
#         }
#         for item in query:
#             cred['usernames'][item.username] = {
#                 "email": item.email,
#                 "name": item.name,
#                 "password": item.password
#         }
#         for item in query:
#             names.append(item.name)
#             usernames.append(item.username)
#             passwords.append(item.password)
#             emails.append(item.email)
#         for item in queryPredefined:
#             predefinedEmail.append(item.email)
#         authenticator = stauth.Authenticate(cred, "performance_dashboard", "abcde", preauthorized=predefinedEmail)
#     except Exception as e:
#         st.error(f'Ada masalah saat menyiapkan auth, pesan: {e}')
#     finally:
#         session.close()
# # ----------------------------- section streamlit front end --------------------------------------
#     st.subheader("Login and Signup Page", divider=True)
#     pageMenu = st.selectbox("Pilih Menu", ["Login", "Signup"])
#     authentication_status = False # ditambahkan agar line 109 tdk error
#     if pageMenu == "Login":
#         name, authentication_status, username = authenticator.login("login", "main")
#         if authentication_status:
#             st.info(f'Selamat datang :blue[{name}]')
#             authenticator.logout('Logout', 'main', key='abcde')
#         if authentication_status is False:
#             st.error('Username/password is incorrect')
#         elif authentication_status is None:
#             st.warning('Please enter your username and password')
#     elif pageMenu == "Signup":
#         with st.form("signup_form"):
#             st.write("Register User")
#             email_val = st.text_input("Email")
#             username_val = st.text_input("Username")
#             name_val = st.text_input("Name")
#             pass_val = st.text_input("Password", type="password")
#             pass2_val = st.text_input("Repeat Password", type="password")

#             # Every form must have a submit button.
#             submitted = st.form_submit_button("Signup")
#             if submitted:
#                 try:
#                     hashed_passwords = stauth.Hasher([pass_val]).generate()
#                     entry = user(username=username_val, email=email_val, name=name_val, password=hashed_passwords[0])
#                     session.add(entry)
#                     session.commit()
#                     st.success("User berhasil dibuat")
#                     st.balloons()
#                 except Exception as e:
#                     st.error(f'ada masalah saat menambahkan user, pesan: {e}')
#                 finally:
#                     session.close()
# # ----------------------- Admin Previelege -----------------------------
#     if authentication_status and username == "admin3": 
#         st.header(":green[Administrator] Menu", divider=True)
#         st.info("Hanya admin yang dapat melihat menu dibawah")
# # ---------------- Akun terdaftar menu -------------------
#         st.subheader("Akun yang terdaftar", divider=True)
#         akunTerdaftarList = {
#             "username": usernames,
#             "name": names,
#             "email": emails,
#             "password": passwords
#         }
#         st.dataframe(akunTerdaftarList)
# # ---------------- Menambahkan predefined Akun -----------------------
#         st.subheader("Predefined User", divider=True)
#         st.info("Predefined User adalah akun email yang telah diijinkan untuk melakukan registrasi oleh admin")
#         with st.form("predefined_form"):
#             predefinedEmailInput = st.text_input("Masukkan email yang akan diijinkan registrasi user")
#             submitted = st.form_submit_button("Add predefined user")
#             if submitted:
#                 try:
#                     entry = predefinedUser(email=predefinedEmailInput)
#                     session.add(entry)
#                     session.commit()
#                     st.success("User predefined berhasil dibuat")
#                 except Exception as e:
#                     st.error(f'Predefined user gagal dibuat, pesan: {e}')
#                 finally:
#                     session.close()
#             for item in queryPredefined:
#                 st.write(item.email)
# except Exception as e:
#     st.error(f'Ada masalah saat pada aplikasi, pesan: {e}')