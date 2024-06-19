import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import pytz

# 데이터베이스 설정
DATABASE_URL = 'sqlite:///schedule.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# 모델 정의
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='schedules')
    period1 = Column(Boolean, default=False)
    period2 = Column(Boolean, default=False)
    period3 = Column(Boolean, default=False)
    period4 = Column(Boolean, default=False)

User.schedules = relationship('Schedule', order_by=Schedule.id, back_populates='user')

Base.metadata.create_all(engine)

# 함수 정의
def get_schedule(user_id, date):
    schedule = session.query(Schedule).filter_by(user_id=user_id, date=date).first()
    if not schedule:
        schedule = Schedule(user_id=user_id, date=date)
        session.add(schedule)
        session.commit()
    return schedule

def authenticate(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and user.password == password:
        return True
    return False

def register(username, password):
    if session.query(User).filter_by(username=username).first():
        return False
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return True

# 날짜 변경 확인 및 데이터 초기화
def reset_schedules():
    today = datetime.now(pytz.timezone('Europe/Berlin')).date()
    yesterday = today - timedelta(days=1)
    schedules = session.query(Schedule).filter_by(date=yesterday).all()
    for schedule in schedules:
        schedule.period1 = False
        schedule.period2 = False
        schedule.period3 = False
        schedule.period4 = False
    session.commit()

# Streamlit 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# Streamlit 앱
st.title("Schedule Checker")

# 사용자 인증 및 회원가입
if not st.session_state.authenticated:
    auth_mode = st.radio("Choose an option", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Login":
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    else:
        if st.button("Sign Up"):
            if register(username, password):
                st.success("User registered successfully")
            else:
                st.error("Username already exists")
else:
    # 날짜 변경 확인 및 데이터 초기화
    reset_schedules()

    # 사용자 정보 가져오기
    user = session.query(User).filter_by(username=st.session_state.user).first()

    # 날짜 설정
    today = datetime.now(pytz.timezone('Europe/Berlin')).date()
    schedule = get_schedule(user.id, today)

    # 메모장 UI
    st.subheader(f"{user.username}의 오늘 수업 일정")
    period1 = st.checkbox("1교시", schedule.period1)
    period2 = st.checkbox("2교시", schedule.period2)
    period3 = st.checkbox("3교시", schedule.period3)
    period4 = st.checkbox("4교시", schedule.period4)

    # 자동 저장
    if period1 != schedule.period1 or \
       period2 != schedule.period2 or \
       period3 != schedule.period3 or \
       period4 != schedule.period4:
        schedule.period1 = period1
        schedule.period2 = period2
        schedule.period3 = period3
        schedule.period4 = period4
        session.commit()
        st.success("Schedule saved")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.experimental_rerun()
