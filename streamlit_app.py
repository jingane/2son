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

# 사용자 등록
def add_user(username):
    existing_user = session.query(User).filter_by(username=username).first()
    if not existing_user:
        new_user = User(username=username)
        session.add(new_user)
        session.commit()

add_user("sohn1")
add_user("sohn2")

# 함수 정의
def get_schedule(user_id, date):
    schedule = session.query(Schedule).filter_by(user_id=user_id, date=date).first()
    if not schedule:
        schedule = Schedule(user_id=user_id, date=date)
        session.add(schedule)
        session.commit()
    return schedule

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

# Streamlit 앱
st.title("Schedule Checker")

# 날짜 변경 확인 및 데이터 초기화
reset_schedules()

# 날짜 설정
today = datetime.now(pytz.timezone('Europe/Berlin')).date()

# 사용자 정보 가져오기
sohn1 = session.query(User).filter_by(username="sohn1").first()
sohn2 = session.query(User).filter_by(username="sohn2").first()

# sohn1 일정 가져오기
sohn1_schedule = get_schedule(sohn1.id, today)

# sohn2 일정 가져오기
sohn2_schedule = get_schedule(sohn2.id, today)

# 메모장 UI
col1, col2 = st.columns(2)
with col1:
    st.subheader("sohn1 수업 일정")
    sohn1_period1 = st.checkbox("1교시", sohn1_schedule.period1, key="sohn1_period1")
    sohn1_period2 = st.checkbox("2교시", sohn1_schedule.period2, key="sohn1_period2")
    sohn1_period3 = st.checkbox("3교시", sohn1_schedule.period3, key="sohn1_period3")
    sohn1_period4 = st.checkbox("4교시", sohn1_schedule.period4, key="sohn1_period4")

with col2:
    st.subheader("sohn2 수업 일정")
    sohn2_period1 = st.checkbox("1교시", sohn2_schedule.period1, key="sohn2_period1")
    sohn2_period2 = st.checkbox("2교시", sohn2_schedule.period2, key="sohn2_period2")
    sohn2_period3 = st.checkbox("3교시", sohn2_schedule.period3, key="sohn2_period3")
    sohn2_period4 = st.checkbox("4교시", sohn2_schedule.period4, key="sohn2_period4")

# 자동 저장
if sohn1_period1 != sohn1_schedule.period1 or \
   sohn1_period2 != sohn1_schedule.period2 or \
   sohn1_period3 != sohn1_schedule.period3 or \
   sohn1_period4 != sohn1_schedule.period4:
    sohn1_schedule.period1 = sohn1_period1
    sohn1_schedule.period2 = sohn1_period2
    sohn1_schedule.period3 = sohn1_period3
    sohn1_schedule.period4 = sohn1_period4
    session.commit()
    st.success("sohn1 일정 저장됨")

if sohn2_period1 != sohn2_schedule.period1 or \
   sohn2_period2 != sohn2_schedule.period2 or \
   sohn2_period3 != sohn2_schedule.period3 or \
   sohn2_period4 != sohn2_schedule.period4:
    sohn2_schedule.period1 = sohn2_period1
    sohn2_schedule.period2 = sohn2_period2
    sohn2_schedule.period3 = sohn2_period3
    sohn2_schedule.period4 = sohn2_period4
    session.commit()
    st.success("sohn2 일정 저장됨")
