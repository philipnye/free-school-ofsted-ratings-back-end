-- ADMIN TOTALS
select
  Max(Run_date),
  Run_date_short,
  NumberOfSchools,
  NumberOfClosedSchools,
  NumberOfUnopenedSchools,
  NumberOfOpenUninspectedSchools,
  NumberOfOpenSec5Schools,
  NumberOfOpenLSSchools
from admin_totals
where
  Spreadsheet_pass='Pass' AND
  Saving_pass='Pass'

-- DATA FOR TABLES
-- Open schools
select
  published_recent,
  inspection_rating2,
  schooltype,
  LA,
  URL,
  schoolname_with_note_symbol,
  URN,
  schoolname,
  open_closed,
  opendate_full,
  inspection_date_long,
  inspection_rating,
  opendate_short,
  phase,
  publication_date,
  publication_date_long,
  include,
  notes,
  note_symbol,
  inspection_date
from Last_successful_school_details
where
  include=1
order by
  inspection_rating2,
  schoolname

-- Closed schools
select
  published_recent,
  inspection_rating2,
  schooltype,
  LA,
  URL,
  schoolname_with_note_symbol,
  URN,
  schoolname,
  open_closed,
  opendate_full,
  inspection_date_long,
  inspection_rating,
  opendate_short,
  phase,
  publication_date,
  publication_date_long,
  include,
  notes,
  note_symbol,
  inspection_date
from Last_successful_school_details
where
  open_closed='Closed'
order by
  inspection_rating2,
  schoolname

-- DATA FOR PIE CHARTS
-- Overall
select
  ID,
  ratingtype,
  ratingname,
  rating,
  percentage,
  ratingcount
from Last_successful_ratings_summary
where
  ratingtype='Overall' AND
  percentage>0
order by rating

-- Primary
select
  ID,
  ratingtype,
  ratingname,
  rating,
  percentage,
  ratingcount
from Last_successful_ratings_summary
where
  ratingtype='Primary' AND
  percentage>0
order by rating

-- Secondary
select
  ID,
  ratingtype,
  ratingname,
  rating,
  percentage,
  ratingcount
from Last_successful_ratings_summary
where
  ratingtype='Secondary' AND
  percentage>0
order by rating

-- ALl-through
select
  ID,
  ratingtype,
  ratingname,
  rating,
  percentage,
  ratingcount
from Last_successful_ratings_summary
where
  ratingtype='All-through' AND
  percentage>0
order by rating

-- Alternative provision
select
  ID,
  ratingtype,
  ratingname,
  rating,
  percentage,
  ratingcount
from Last_successful_ratings_summary
where
  ratingtype='Alternative provision' AND
  percentage>0
order by rating

-- Special
select
  ID,
  ratingtype,
  ratingname,
  rating,
  percentage,
  ratingcount
from Last_successful_ratings_summary
where
  ratingtype='Special' AND
  percentage>0
order by rating



-- REFACTOR
-- PULL OUT KEY FIGURES
-- Most recent
select
    Max(Run_date), *
from log

-- Previous
select
    Max(Run_date), *
from log
WHERE Run_date < (SELECT MAX(Run_date) FROM log)

-- One week ago
select
    *
from log
where date(Run_date)=date('now','-7 days');

-- Last successful
select
    Max(Run_date), *
from log
where
    Spreadsheet_pass="Pass" AND
    Saving_pass="Pass"


-- TEST PRODUCING RATING PERCENTAGES
select
    phase,
    inspection_rating,
    count(1) count,
    count(1)*100/(
        select count(1)
        from inspections
        where
            inspection_rating is not 'n/a' and
            inspection_rating is not 'Learning and skills inspection - findings not scraped' and
            phase='Primary' and
            open_closed='Open') percentage
from inspections
where
    inspection_rating is not 'n/a'
    and inspection_rating is not 'Learning and skills inspection - findings not scraped'
    and phase='Primary'
    and open_closed='Open'
group by
    inspection_rating
order by
    inspection_rating;

SQLITE WAY OF DOING PARTITION() OVER, TO FIND LATEST INSPECTION RECORD FOR EACH URN
select
  q.*
from inspections q
    join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s
        on
          q.urn= s.urn and
          q.inspection_date_long = s.max_date
group by q.urn
