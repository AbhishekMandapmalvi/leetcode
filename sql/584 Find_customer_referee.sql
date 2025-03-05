SELECT name
FROM Customer
where (referee_id is NULL) OR (referee_id != 2);