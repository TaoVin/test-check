-- 查询原始ksql
SELECT m.fnumber    AS 物料编码,
       m.fname      AS 物料名称,
       m.fmodel     AS 规格,
       m.fk_sn15_pp AS 品牌,
       m.foldnumber AS 旧物料编码
FROM t_bd_material m
         INNER JOIN (SELECT fname,
                            fmodel,
                            fk_sn15_pp
                     FROM (SELECT fname,
                                  fmodel,
                                  fk_sn15_pp,
                                  count(DISTINCT fnumber) AS num
                           FROM t_bd_material
                           GROUP BY fname, fmodel, fk_sn15_pp) c
                     WHERE num > 1) b ON m.fname = b.fname
    AND m.fmodel = b.fmodel
    AND m.fk_sn15_pp = b.fk_sn15_pp
ORDER BY m.fname, m.fmodel, m.fk_sn15_pp;