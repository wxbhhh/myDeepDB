SELECT count(*) FROM cast_info ci WHERE true AND ci.role_id=1; 4.67
SELECT count(distinct(ci.id))FROM cast_info ci WHERE true AND ci.role_id=1; 4.78
SELECT count(distinct(ci.person_id)) FROM cast_info ci WHERE true AND ci.role_id=1; 98.6
SELECT count(distinct(ci.movie_id)) FROM cast_info ci WHERE true AND ci.role_id=1;
SELECT count(distinct(ci.role_id)) FROM cast_info ci WHERE true AND ci.role_id=1;

SELECT count(*), count(distinct(ci.id)), count(distinct(ci.person_id)), count(distinct(ci.movie_id)), count(distinct(ci.role_id)) FROM cast_info ci WHERE true AND ci.role_id=1;
125.6