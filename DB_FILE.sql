create database Hospital;
use Hospital;
create table Doctor (drId int8 primary key auto_increment,drName varchar(35),drEmail varchar(50),drPassword varchar(10));
alter table Doctor add drGender varchar(8);

create table Patient (ptId int8 primary key auto_increment,ptName varchar(35),ptEmail varchar(50),ptPassword varchar(10));
alter table Patient add ptGender varchar(8);

create table Appointments (apId int8 primary key auto_increment, ptId int8, drId int8,apDate varchar(20),apTime varchar(10),apTitle varchar(30),apTotal int8,apBalance int8);
desc Appointments;
select * from Appointments;

SELECT apDay, COUNT(*) as Count FROM Appointments where drId = GROUP BY apDay;


alter table Appointments add apTitle varchar(50);

truncate Appointments;
truncate Doctor;
truncate Patient;
truncate Pfav;

create table Pfav (id int8 primary key auto_increment, ptId int8 , drId int8);


create table Dfav (id int8 primary key auto_increment, ptId int8 , drId int8);

drop table Pfav;
select * from Pfav;
truncate table Pfav;
select * from Doctor;

select D.drEmail , P.ptEmail from Doctor d , Patient P where drEmail='manikaraj480@gmail.com' or ptEmail='manikaraj480@gmail.com'; 
desc Doctor;

truncate table Doctor;
desc Doctor;

select * from Patient;