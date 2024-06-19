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
    if not session.query(User).filter_by(username=username).first():
        user = User(username=username)
        session.add(user)
        session.commit()

add_user("아들 1")
add_user("아들 2")

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
son1 = session.query(User).filter_by(username="아들 1").first()
son2 = session.query(User).filter_by(username="아들 2").first()

# 아들 1 일정 가져오기
son1_schedule = get_schedule(son1.id, today)

# 아들 2 일정 가져오기
son2_schedule = get_schedule(son2.id, today)

# 메모장 UI
col1, col2 = st.columns(2)
with col1:
    st.subheader("아들 1 수업 일정")
    son1_period1 = st.checkbox("1교시", son1_schedule.period1, key="son1_period1")
    son1_period2 = st.checkbox("2교시", son1_schedule.period2, key="son1_period2")
    son1_period3 = st.checkbox("3교시", son1_schedule.period3, key="son1_period3")
    son1_period4 = st.checkbox("4교시", son1_schedule.period4, key="son1_period4")

with col2:
    st.subheader("아들 2 수업 일정")
    son2_period1 = st.checkbox("1교시", son2_schedule.period1, key="son2_period1")
    son2_period2 = st.checkbox("2교시", son2_schedule.period2, key="son2_period2")
    son2_period3 = st.checkbox("3교시", son2_schedule.period3, key="son2_period3")
    son2_period4 = st.checkbox("4교시", son2_schedule.period4, key="son2_period4")

# 자동 저장
if son1_period1 != son1_schedule.period1 or \
   son1_period2 != son1_schedule.period2 or \
   son1_period3 != son1_schedule.period3 or \
   son1_period4 != son1_schedule.period4:
    son1_schedule.period1 = son1_period1
    son1_schedule.period2 = son1_period2
    son1_schedule.period3 = son1_period3
    son1_schedule.period4 = son1_period4
    session.commit()
    st.success("아들 1 일정 저장됨")

if son2_period1 != son2_schedule.period1 or \
   son2_period2 != son2_schedule.period2 or \
   son2_period3 != son2_schedule.period3 or \
   son2_period4 != son2_schedule.period4:
    son2_schedule.period1 = son2_period1
    son2_schedule.period2 = son2_period2
    son2_schedule.period3 = son2_period3
    son2_schedule.period4 = son2_period4
    session.commit()
    st.success("아들 2 일정 저장됨")
