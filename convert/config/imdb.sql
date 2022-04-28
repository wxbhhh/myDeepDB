CREATE TABLE aka_name (
    id integer NOT NULL PRIMARY KEY,
    person_id integer NOT NULL,
    name varchar(50),
    imdb_index varchar(3),
    name_pcode_cf varchar(11),
    name_pcode_nf varchar(11),
    surname_pcode varchar(11),
    md5sum varchar(65)
);

CREATE TABLE aka_title (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer NOT NULL,
    title varchar(50),
    imdb_index varchar(4),
    kind_id integer NOT NULL,
    production_year integer,
    phonetic_code varchar(5),
    episode_of_id integer,
    season_nr integer,
    episode_nr integer,
    note varchar(72),
    md5sum varchar(32)
);

CREATE TABLE cast_info (
    id integer NOT NULL PRIMARY KEY,
    person_id integer NOT NULL,
    movie_id integer NOT NULL,
    person_role_id integer,
    note varchar(50),
    nr_order integer,
    role_id integer NOT NULL
);

CREATE TABLE char_name (
    id integer NOT NULL PRIMARY KEY,
    name varchar(50) NOT NULL,
    imdb_index varchar(2),
    imdb_id integer,
    name_pcode_nf varchar(5),
    surname_pcode varchar(5),
    md5sum varchar(32)
);

CREATE TABLE comp_cast_type (
    id integer NOT NULL PRIMARY KEY,
    kind varchar(32) NOT NULL
);

CREATE TABLE company_name (
    id integer NOT NULL PRIMARY KEY,
    name varchar(50) NOT NULL,
    country_code varchar(6),
    imdb_id integer,
    name_pcode_nf varchar(5),
    name_pcode_sf varchar(5),
    md5sum varchar(32)
);

CREATE TABLE company_type (
    id integer NOT NULL PRIMARY KEY,
    kind varchar(32)
);

CREATE TABLE complete_cast (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer,
    subject_id integer NOT NULL,
    status_id integer NOT NULL
);

CREATE TABLE info_type (
    id integer NOT NULL PRIMARY KEY,
    info varchar(32) NOT NULL
);

CREATE TABLE keyword (
    id integer NOT NULL PRIMARY KEY,
    keyword varchar(50) NOT NULL,
    phonetic_code varchar(5)
);

CREATE TABLE kind_type (
    id integer NOT NULL PRIMARY KEY,
    kind varchar(15)
);

CREATE TABLE link_type (
    id integer NOT NULL PRIMARY KEY,
    link varchar(32) NOT NULL
);

CREATE TABLE movie_companies (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer NOT NULL,
    company_id integer NOT NULL,
    company_type_id integer NOT NULL,
    note varchar(50)
);

CREATE TABLE movie_info_idx (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer NOT NULL,
    info_type_id integer NOT NULL,
    info varchar(50) NOT NULL,
    note varchar(1)
);

CREATE TABLE movie_keyword (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer NOT NULL,
    keyword_id integer NOT NULL
);

CREATE TABLE movie_link (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer NOT NULL,
    linked_movie_id integer NOT NULL,
    link_type_id integer NOT NULL
);

CREATE TABLE name (
    id integer NOT NULL PRIMARY KEY,
    name varchar(50) NOT NULL,
    imdb_index varchar(9),
    imdb_id integer,
    gender varchar(1),
    name_pcode_cf varchar(5),
    name_pcode_nf varchar(5),
    surname_pcode varchar(5),
    md5sum varchar(32)
);

CREATE TABLE role_type (
    id integer NOT NULL PRIMARY KEY,
    role varchar(32) NOT NULL
);

CREATE TABLE title (
    id integer NOT NULL PRIMARY KEY,
    title varchar(50) NOT NULL,
    imdb_index varchar(5),
    kind_id integer NOT NULL,
    production_year integer,
    imdb_id integer,
    phonetic_code varchar(5),
    episode_of_id integer,
    season_nr integer,
    episode_nr integer,
    series_years varchar(49),
    md5sum varchar(32)
);

CREATE TABLE movie_info (
    id integer NOT NULL PRIMARY KEY,
    movie_id integer NOT NULL,
    info_type_id integer NOT NULL,
    info varchar(50) NOT NULL,
    note varchar(50)
);

CREATE TABLE person_info (
    id integer NOT NULL PRIMARY KEY,
    person_id integer NOT NULL,
    info_type_id integer NOT NULL,
    info varchar(50) NOT NULL,
    note varchar(50)
);

-- 添加约束关系
-- aka_name
create index aka_name_idx_md5 on aka_name(md5sum);
create index aka_name_idx_name on aka_name(name);
create index aka_name_idx_pcode on aka_name(surname_pcode);

-- aka_title
create index aka_title_idx_epof on aka_title(episode_of_id);
create index aka_title_idx_kindid on aka_title(kind_id);
create index aka_title_idx_md5 on aka_title(md5sum);
create index aka_title_idx_movieid on aka_title(movie_id);
create index aka_title_idx_pcode on aka_title(phonetic_code);
create index aka_title_idx_title on aka_title(title);
create index aka_title_idx_year on aka_title(production_year);

-- cast_info
create index cast_info_idx_cid on cast_info (person_role_id);
create index cast_info_idx_mid on cast_info (movie_id);
create index cast_info_idx_pid on cast_info (person_id);
create index cast_info_idx_rid on cast_info (role_id);

-- char_name
create index char_name_idx_imdb_id on char_name(imdb_id);
create index char_name_idx_md5 on char_name(md5sum);
create index char_name_idx_name on char_name(name);
create index char_name_idx_pcode on char_name(surname_pcode);
create index char_name_idx_pcodenf on char_name(name_pcode_nf);

-- comp_cast_type
create index comp_cast_type_kind on comp_cast_type (kind);

-- company_name
create index company_name_idx_ccode on company_name (country_code);
create index company_name_idx_imdb_id on company_name (imdb_id);
create index company_name_idx_md5 on company_name (md5sum);
create index company_name_idx_name on company_name (name);
create index company_name_idx_pcodenf on company_name (name_pcode_nf);
create index company_name_idx_pcodesf on company_name (name_pcode_sf);

-- company_type
create index company_type_kind on company_type (kind);

-- complete_cast
create index complete_cast_idx_mid on complete_cast (movie_id);
create index complete_cast_idx_sid on complete_cast (subject_id);

-- info_type
create index complete_cast_idx_sid on complete_cast (subject_id);

-- keyword
create index keyword_idx_keyword on keyword (keyword);
create index keyword_idx_pcode on keyword (phonetic_code);

-- kind_type
create index kind_type_kind on kind_type (kind);

-- link_type
create index link_type_link on link_type (link);

-- movie_companies
create index movie_companies_idx_cid on movie_companies (company_id);
create index movie_companies_idx_ctypeid on movie_companies (company_type_id);
create index movie_companies_idx_mid on movie_companies (movie_id);

-- movie_info
create index movie_info_idx_infotypeid on movie_info (info_type_id);
create index movie_info_idx_mid on movie_info (movie_id);

-- movie_keyword
create index movie_keyword_idx_keywordid on movie_keyword (keyword_id);
create index movie_keyword_idx_mid on movie_keyword (movie_id);

-- movie_link
create index movie_link_idx_lmid on movie_link (linked_movie_id);
create index movie_link_idx_ltypeid on movie_link (link_type_id);
create index movie_link_idx_mid on movie_link (movie_id);

-- name
create index name_idx_gender on name (gender);
create index name_idx_imdb_id on name (imdb_id);
create index name_idx_md5 on name (md5sum);
create index name_idx_name on name (name);
create index name_idx_pcode on name (surname_pcode);
create index name_idx_pcodecf on name (name_pcode_cf);
create index name_idx_pcodenf on name (name_pcode_nf);

-- person_id
create index person_info_idx_itypeid on person_info (info_type_id);
create index person_info_idx_pid on person_info (person_id);

-- role_type
create index role_type_role on role_type (role);

-- title
create index title_idx_episode_nr on title (episode_nr);
create index title_idx_epof on title (episode_of_id);
create index title_idx_imdb_id on title (imdb_id);
create index title_idx_kindid on title (kind_id);
create index title_idx_md5 on title (md5sum);
create index title_idx_pcode on title (phonetic_code);
create index title_idx_season_nr on title (season_nr);
create index title_idx_title on title (title);
create index title_idx_year on title (production_year);


-- 以下为精简后用到的索引
-- -----------------------------------------------------------------------
-- -----------------------------------------------------------------------
-- cast_info
create index cast_info_idx_mid on cast_info (movie_id);
create index cast_info_idx_pid on cast_info (person_id);
create index cast_info_idx_rid on cast_info (role_id);


-- movie_companies
create index movie_companies_idx_cid on movie_companies (company_id);
create index movie_companies_idx_ctypeid on movie_companies (company_type_id);
create index movie_companies_idx_mid on movie_companies (movie_id);

-- movie_info
create index movie_info_idx_infotypeid on movie_info (info_type_id);
create index movie_info_idx_mid on movie_info (movie_id);

-- movie_info_idx
create index movie_info_idx_idx_infotypeid on movie_info_idx (info_type_id);
create index movie_info_idx_idx_mid on movie_info_idx (movie_id);

-- movie_keyword
create index movie_keyword_idx_keywordid on movie_keyword (keyword_id);
create index movie_keyword_idx_mid on movie_keyword (movie_id);

-- title
create index title_idx_kindid on title (kind_id);
create index title_idx_year on title (production_year);