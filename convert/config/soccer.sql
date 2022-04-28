-- 查看所有的表
-- SELECT name _id FROM sqlite_master WHERE type ='table'

-- o_country数据插入m_country
-- insert into m_country(id, name) select id, name from o_Country ;

-- o_player数据插入m_player
-- insert into m_player(id, name, height, weight) select player_api_id, player_name, height, weight from o_Player  ;

-- o_player_stats数据插入m_player_stats
-- insert into m_player_stats(player_id, stat_date, potential, overall_rating)
--   select player_api_id, strftime('%Y%m%d', date_stat), potential, overall_rating from o_Player_Stats  ;

-- o_team数据插入m_team
-- insert into m_team(id, long_name, short_name) select team_api_id, team_long_name, team_short_name from o_Team  ;

-- o_match数据插入m_match
-- insert into m_match(match_date, country_id, home_team_id, home_team_captain, away_team_id, away_team_captain)
--     select strftime('%Y%m%d', date), country_id, home_team_api_id, home_player_1, away_team_api_id, away_player_1 from o_Match
--         where o_Match.away_player_1 is not null and o_Match.home_player_1 is not null;

-- select count(*) from m_match, m_team where m_match.away_team_id = m_team.id;

-- select count(*) from m_match, m_player where m_match.away_team_captain = m_player.id;

select count(distinct(m_player.id)) from m_player, m_player_stats where m_player.id = m_player_stats.player_id;