drop table if exists users;
create table users(
  id integer primary key autoincrement,
  username text not null,
  password text not null,
  currentScore int
);

drop table if exists playthrough;
create table playthrough(
  id integer primary key autoincrement,
  score integer,
  gameid text,
  playerid integer,
  foreign key  (playerid) references users(id)
);
