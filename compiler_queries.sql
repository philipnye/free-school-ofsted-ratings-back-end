-- INPUT DATA FOR SCRAPER
select
    URN,
    LAEstab,
    school_name,
    note_symbol,
    notes,
    school_name_with_note_symbol,
    LA,
    school_type,
    phase,
    open_closed,
    open_date,
    close_date,
    inspection_rating,
    inspection_rating_text,
    publication_date,
    publication_date_long,
    inspection_date,
    inspection_date_long,
    URL
from School_details
where
    school_type in ('Free schools','Free schools alternative provision','Free schools special','Free schools 16 to 19')
