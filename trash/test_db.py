from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from util.common_tools import bin_to_array, array_to_bin
import numpy as np

Base = declarative_base()


class ManageUser(Base):
    __tablename__ = 'manage_users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(20), nullable=False)

    def __repr__(self):
        return "<ManageUser(id='%s', username='%s', password='%s')>" \
               % (self.id, self.username, self.password)


class AttendanceUser(Base):
    __tablename__ = 'attendance_user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    photo_id = Column(Integer, ForeignKey("photo.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("feature.id"), nullable=False)
    attendance_id = Column(Integer, ForeignKey("attendance.id"), nullable=False)

    photo = relationship("Photo")
    feature = relationship("Feature")
    attendance = relationship("Attendance", backref="user_list")

    def __repr__(self):
        return "<AttendanceUser(id='%s', name='%s', attendance_id='%s')>" \
               % (self.id, self.name, self.attendance_id)


class AttendanceRecord(Base):
    __tablename__ = 'attendance_record'

    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, ForeignKey('photo.id'), nullable=False)
    feature_id = Column(Integer, ForeignKey("feature.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("attendance_user.id"), nullable=False)
    attendance_id = Column(Integer, ForeignKey("attendance.id"), nullable=False)

    photo = relationship("Photo")
    feature = relationship("Feature")
    user = relationship("AttendanceUser", backref="record_list")
    attendance = relationship("Attendance", backref="record_list")

    def __repr__(self):
        return "<AttendanceRecord(id='%s', user_id='%s', attendance_id='%s')>" \
               % (self.id, self.user_id, self.attendance_id)


class AttendanceDate(Base):
    __tablename__ = 'attendance_date'

    id = Column(Integer, primary_key=True)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    attendance_id = Column(Integer, ForeignKey('attendance.id'), nullable=False)

    attendance = relationship("Attendance", backref="date_list")

    def __repr__(self):
        return "<AttendanceDate(id='%s', attendance_id='%s')>" \
               % (self.id, self.attendance_id)


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    src_path = Column(String(500), nullable=False)

    def __repr__(self):
        return "<AttendanceDate(id='%s', src_path='%s')>" \
               % (self.id, self.src_path)


class Feature(Base):
    __tablename__ = 'feature'

    id = Column(Integer, primary_key=True)
    data = Column(LargeBinary, nullable=False)
    photo_id = Column(Integer, ForeignKey('photo.id'))

    photo = relationship("Photo")

    def __repr__(self):
        return "<AttendanceDate(id='%s', data_len='%s')>" \
               % (self.id, len(self.data))


class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('manage_users.id'))
    title = Column(String(200), nullable=False)
    type = Column(Integer, nullable=False)
    info = Column(String(500))

    creator_user = relationship("ManageUser", backref="attendance_list")

    def __repr__(self):
        return "<AttendanceRecord(id='%s', creator_id='%s', title='%s')>" \
               % (self.id, self.creator_id, self.title)


def init_db():
    username = 'root'
    password = '109412'
    host = '127.0.0.1'
    port = 3306
    db = 'face'

    connect_str = 'mysql+mysqldb://{}:{}@{}:{}/{}' \
        .format(username, password, host, port, db)

    engine = create_engine(connect_str, echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()


def fake_data(session):
    manager = ManageUser(username="fish", password="123456")
    attendance = Attendance(title="noon", type=1)
    attendance_date = AttendanceDate(start_time=0, end_time=60)
    attendance_user = AttendanceUser(name="cat")
    attendance_record = AttendanceRecord()
    photo = Photo(src_path="/home/fish/PycharmProjects/Web&FaceRecognize/upload_image/Obama.jpg")
    feature = Feature(data=array_to_bin(np.arange(512)))

    attendance.creator_user = manager

    attendance_date.attendance = attendance

    attendance_user.attendance = attendance
    attendance_user.photo = photo
    attendance_user.feature = feature

    attendance_record.user = attendance_user
    attendance_record.attendance = attendance
    attendance_record.feature = feature
    attendance_record.photo = photo

    feature.photo = photo

    session.add_all([
        manager
    ])

    print(session.new)

    session.commit()

    print(attendance.record_list)
    print(attendance.date_list)
    print(attendance_user.record_list)
    print(manager.attendance_list)


if __name__ == '__main__':
    session = init_db()
    fake_data(session)
