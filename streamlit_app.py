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

add_user("큰아들")
add_user("작은아들")

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

# Streamlit 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True

# Streamlit 앱
st.title("Schedule Checker")

# 날짜 변경 확인 및 데이터 초기화
reset_schedules()

# 날짜 설정
today = datetime.now(pytz.timezone('Europe/Berlin')).date()

# 사용자 정보 가져오기
big_son = session.query(User).filter_by(username="큰아들").first()
little_son = session.query(User).filter_by(username="작은아들").first()

# 큰아들 일정 가져오기
big_son_schedule = get_schedule(big_son.id, today)

# 작은아들 일정 가져오기
little_son_schedule = get_schedule(little_son.id, today)
# 메모장 UI
col1, col2 = st.columns(2)
with col1:
    st.subheader("큰아들 수업 일정")
    big_son_period1 = st.checkbox("1교시", big_son_schedule.period1, key="big_son_period1")
    big_son_period2 = st.checkbox("2교시", big_son_schedule.period2, key="big_son_period2")
    big_son_period3 = st.checkbox("3교시", big_son_schedule.period3, key="big_son_period3")
    big_son_period4 = st.checkbox("4교시", big_son_schedule.period4, key="big_son_period4")

with col2:
    st.subheader("작은아들 수업 일정")
    little_son_period1 = st.checkbox("1교시", little_son_schedule.period1, key="little_son_period1")
    little_son_period2 = st.checkbox("2교시", little_son_schedule.period2, key="little_son_period2")
    little_son_period3 = st.checkbox("3교시", little_son_schedule.period3, key="little_son_period3")
    little_son_period4 = st.checkbox("4교시", little_son_schedule.period4, key="little_son_period4")

# 자동 저장
if big_son_period1 != big_son_schedule.period1 or \
   big_son_period2 != big_son_schedule.period2 or \
   big_son_period3 != big_son_schedule.period3 or \
   big_son_period4 != big_son_schedule.period4:
    big_son_schedule.period1 = big_son_period1
    big_son_schedule.period2 = big_son_period2
    big_son_schedule.period3 = big_son_period3
    big_son_schedule.period4 = big_son_period4
    session.commit()
    st.success("큰아들 일정 저장됨")

if little_son_period1 != little_son_schedule.period1 or \
   little_son_period2 != little_son_schedule.period2 or \
   little_son_period3 != little_son_schedule.period3 or \
   little_son_period4 != little_son_schedule.period4:
    little_son_schedule.period1 = little_son_period1
    little_son_schedule.period2 = little_son_period2
    little_son_schedule.period3 = little_son_period3
    little_son_schedule.period4 = little_son_period4
    session.commit()
    st.success("작은아들 일정 저장됨")
