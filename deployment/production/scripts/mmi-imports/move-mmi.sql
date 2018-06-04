insert into gis.public.realtime_earthquakemmicontour (earthquake_id, mmi, geometry, properties)
    select realtime_earthquake.id, c.mmi, st_linemerge(c.geometry),
        '{'||concat_ws(',','"MMI":'||c.mmi,'"X":'||c.x,'"Y":'||c.y,'"RGB":"'||c.rgb||'"','"ALIGN":"'||c.align||'"','"VALIGN":"'||c.valign||'"','"LEN":'||c.len,'"ROMAN":'||coalesce('"'||c.roman||'"', 'null'))||'}' from gis.public.table_contour as c inner join realtime_earthquake on cast(c.shake_id as Text) = realtime_earthquake.shake_id;
