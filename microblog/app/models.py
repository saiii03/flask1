from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import datetime,timezone
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

followers_table=sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id',sa.Integer,sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id',sa.Integer,sa.ForeignKey('user.id'),
              primary_key=True)
)

class User (UserMixin,db.Model):
    id: so.Mapped[int]=so.mapped_column(primary_key=True)
    username:so.Mapped[str]=so.mapped_column(sa.String(126),index=True,unique=True)
    email:so.Mapped[str]=so.mapped_column(sa.String(126),index=True,unique=True)
    password_hash:so.Mapped[Optional[str]]=so.mapped_column(sa.String(126))

    posts: so.WriteOnlyMapped['Post']=so.relationship(back_populates="author")
    about_me: so.Mapped[Optional[str]]=so.mapped_column(sa.String(146))
    last_seen:so.Mapped[Optional[datetime]]=so.mapped_column(default=lambda: datetime.now(timezone.utc))

    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers_table,
        primaryjoin=(followers_table.c.followed_id == id),
        secondaryjoin=(followers_table.c.follower_id == id),
        back_populates='following',
        lazy='dynamic'
    )

    # Define following relationship (users this user follows)
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers_table,
        primaryjoin=(followers_table.c.follower_id == id),
        secondaryjoin=(followers_table.c.followed_id == id),
        back_populates='followers',
        lazy='dynamic'
    )

    def follow(self,user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self,user):
        query=self.following.select().where(user.id==user.id)
        return db.session.scalar(query) is not None
    
    def followers_count(self):
        query=sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)
    
    def following_count(self):
        query=sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)




    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    
    def set_password(self, password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar (self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    

    

    

class Post(db.Model):
    id:so.Mapped[int]=so.mapped_column(primary_key=True)
    body:so.Mapped[str]=so.mapped_column(sa.String(126))
    timestamp:so.Mapped[datetime]= so.mapped_column(index=True,default=lambda:datetime.now(timezone.utc))
    user_id:so.Mapped[int]=so.mapped_column(sa.ForeignKey(User.id),index=True)

    author:so.Mapped[User]=so.relationship(back_populates="posts")

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
@login.user_loader
def load_user(id):
    return db.session.get(User,int(id))

