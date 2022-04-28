origin = SELECT count(*) FROM title t,movie_info_idx mi_idx,movie_keyword mk 
        WHERE t.id=mi_idx.movie_id AND t.id=mk.movie_id 
        AND t.production_year>2005 AND mi_idx.info_type_id=101 ;

parse = SELECT count(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t 
        WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id 
        AND mi_idx.movie_id>=2.0 AND t.id>=2.0 AND t.production_year>2005 
        AND t.id>=1.0 AND mi_idx.info_type_id=101 AND mk.movie_id>=2.0 
        AND mk.movie_id<=2528312.0 AND mi_idx.movie_id<=2525793.0 
        AND mk.movie_id>=1.0 AND t.id<=2528312.0 
        AND mi_idx.movie_id>=1.0 AND mk.movie_id<=2525971.0 
        AND mi_idx.movie_id<=2528312.0 AND t.id<=2525793.0 AND t.id<=2525971.0 ;

原始sql: 
    SELECT count(*) FROM title t,movie_companies mc,cast_info ci 
    WHERE t.id=mc.movie_id AND t.id=ci.movie_id 
    AND mc.company_id=27 AND mc.company_type_id=1 AND ci.person_id<1265390 ;
转化后sql: 
    SELECT count(*) FROM movie_companies mc,cast_info ci,title t 
    WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND 
    mc.company_type_id=1 AND mc.company_id=27 
    AND ci.movie_id>=1.0 AND ci.person_id<1265390 
    AND mc.movie_id<=2525745.0 AND ci.movie_id<=2525975.0 
    AND ci.movie_id<=2528312.0 AND t.id>=2.0 
    AND mc.movie_id>=2.0 AND t.id<=2525975.0 
    AND t.id<=2528312.0 AND mc.movie_id>=1.0 
    AND t.id<=2525745.0 AND mc.movie_id<=2528312.0 AND t.id>=1.0 ;

---------------------------------------------------------------------------------------
title t,movie_companies mc,cast_info ci#t.id=mc.movie_id,t.id=ci.movie_id#mc.company_id,=,27,t.id,>,1000000,mc.company_type_id,=,1,ci.person_id,<,1265390#96573'

原始sql: 
    SELECT count(*) FROM title t,movie_companies mc,cast_info ci 
    WHERE t.id=mc.movie_id AND t.id=ci.movie_id 
    AND mc.company_id=27 AND t.id>1000000 
    AND mc.company_type_id=1 AND ci.person_id<1265390 ;
转化后sql: 
    SELECT count(*) FROM cast_info ci,title t,movie_companies mc 
    WHERE t.id=mc.movie_id AND t.id=ci.movie_id 
    AND ci.person_id<1265390 AND t.id<=2525975.0 
    AND mc.movie_id<=2528312.0 AND mc.movie_id>=1.0 
    AND ci.movie_id<=2525975.0 AND t.id<=2528312.0 
    AND mc.company_type_id=1 AND ci.movie_id<=2528312.0 
    AND mc.movie_id<=2525745.0 AND t.id<=2525745.0 
    AND mc.company_id=27 AND ci.movie_id>=1.0 
    AND mc.movie_id>=2.0 AND t.id>1000000 AND t.id>=1.0 AND t.id>=2.0 ;

原始sql: 
    SELECT count(*) FROM title t,movie_companies mc,cast_info ci 
    WHERE t.id=mc.movie_id AND t.id=ci.movie_id 
    AND mc.company_id=27 AND t.id>1000000 
    AND mc.company_type_id=1 AND ci.person_id<1265390 ;
转化后sql: 
    SELECT count(*) FROM movie_companies mc,cast_info ci,title t 
    WHERE t.id=ci.movie_id AND t.id=mc.movie_id 
    AND t.id<=2525975.0 AND mc.movie_id>1000000 
    AND ci.movie_id<=2528312.0 AND mc.company_id=27 
    AND ci.movie_id<=2525975.0 AND mc.movie_id>=2.0 
    AND mc.movie_id<=2528312.0 AND mc.movie_id<=2525745.0 
    AND ci.person_id<1265390 AND t.id<=2528312.0 
    AND ci.movie_id>1000000 AND mc.movie_id>=1.0 
    AND ci.movie_id>=1.0 AND t.id>=1.0 
    AND t.id<=2525745.0 AND t.id>1000000 
    AND mc.company_type_id=1 AND t.id>=2.0 ;


