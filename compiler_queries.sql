-- INPUT DATA FOR SCRAPER
select
    URN,
    LAEstab,
    schooltype,
    schoolname,
    schoolname_with_note_symbol,
    phase,
    LA,
    open_date,
    inspection_rating,
    inspection_rating2,
    publication_date,
    publication_date_long,
    published_recent,
    inspection_date,
    inspection_date_long,
    URL,
    include,
    open_closed,
    notes,
    note_symbol
from School_details
order by urn
