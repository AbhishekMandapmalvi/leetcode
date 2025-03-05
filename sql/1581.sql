SELECT v.customer_id, COUNT(*) AS count_no_trans
FROM Visits as v
WHERE v.visit_id NOT IN 
(SELECT t.visit_id FROM Transactions AS t)
GROUP BY v.customer_id;