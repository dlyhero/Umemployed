PGDMP      &                |            d2mmc5c51ghegn    16.2     16.4 (Ubuntu 16.4-1.pgdg22.04+1) q   e           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            f           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            g           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            h           1262    26127491    d2mmc5c51ghegn    DATABASE     z   CREATE DATABASE d2mmc5c51ghegn WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';
    DROP DATABASE d2mmc5c51ghegn;
                u2m65eq7rc7j8s    false            i           0    0    DATABASE d2mmc5c51ghegn    ACL     �   REVOKE CONNECT,TEMPORARY ON DATABASE d2mmc5c51ghegn FROM PUBLIC;
GRANT CONNECT ON DATABASE d2mmc5c51ghegn TO heroku_monitor;
GRANT CONNECT ON DATABASE d2mmc5c51ghegn TO heroku_admin;
                   u2m65eq7rc7j8s    false    5224            j           0    0    d2mmc5c51ghegn    DATABASE PROPERTIES     5   ALTER DATABASE d2mmc5c51ghegn CONNECTION LIMIT = 23;
                     u2m65eq7rc7j8s    false                        2615    26133078    _heroku    SCHEMA        CREATE SCHEMA _heroku;
    DROP SCHEMA _heroku;
                heroku_admin    false                        2615    2200    public    SCHEMA     2   -- *not* creating schema, since initdb creates it
 2   -- *not* dropping schema, since initdb creates it
                u2m65eq7rc7j8s    false            k           0    0    SCHEMA public    ACL     +   REVOKE USAGE ON SCHEMA public FROM PUBLIC;
                   u2m65eq7rc7j8s    false    6                        3079    26133099    pg_stat_statements 	   EXTENSION     F   CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;
 #   DROP EXTENSION pg_stat_statements;
                   false    6            l           0    0    EXTENSION pg_stat_statements    COMMENT     u   COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';
                        false    2            ^           1255    26133079    create_ext()    FUNCTION     �  CREATE FUNCTION _heroku.create_ext() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  databaseowner TEXT;

  r RECORD;

BEGIN

  IF tg_tag = 'CREATE EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        CONTINUE WHEN r.command_tag != 'CREATE EXTENSION' OR r.object_type != 'extension';

        schemaname = (
            SELECT n.nspname
            FROM pg_catalog.pg_extension AS e
            INNER JOIN pg_catalog.pg_namespace AS n
            ON e.extnamespace = n.oid
            WHERE e.oid = r.objid
        );

        databaseowner = (
            SELECT pg_catalog.pg_get_userbyid(d.datdba)
            FROM pg_catalog.pg_database d
            WHERE d.datname = current_database()
        );
        --RAISE NOTICE 'Record for event trigger %, objid: %,tag: %, current_user: %, schema: %, database_owenr: %', r.object_identity, r.objid, tg_tag, current_user, schemaname, databaseowner;
        IF r.object_identity = 'address_standardizer_data_us' THEN
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_gaz TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_lex TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_rules TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'amcheck' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.bt_index_check TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.bt_index_parent_check TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'dict_int' THEN
            EXECUTE format('ALTER TEXT SEARCH DICTIONARY %I.intdict OWNER TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'pg_partman' THEN
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.part_config TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.part_config_sub TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.custom_time_partitions TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'pg_stat_statements' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.pg_stat_statements_reset TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'postgis' THEN
            PERFORM _heroku.postgis_after_create();
        ELSIF r.object_identity = 'postgis_raster' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT SELECT ON TABLE %I.raster_columns TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT ON TABLE %I.raster_overviews TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'postgis_topology' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT USAGE ON SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA topology TO %I;', databaseowner);
        ELSIF r.object_identity = 'postgis_tiger_geocoder' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT USAGE ON SCHEMA tiger TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tiger TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tiger TO %I;', databaseowner);

            EXECUTE format('GRANT USAGE ON SCHEMA tiger_data TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tiger_data TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tiger_data TO %I;', databaseowner);
        END IF;
    END LOOP;
  END IF;
END;
$$;
 $   DROP FUNCTION _heroku.create_ext();
       _heroku          heroku_admin    false    7            _           1255    26133080 
   drop_ext()    FUNCTION     �  CREATE FUNCTION _heroku.drop_ext() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  databaseowner TEXT;

  r RECORD;

BEGIN

  IF tg_tag = 'DROP EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_dropped_objects()
    LOOP
      CONTINUE WHEN r.object_type != 'extension';

      databaseowner = (
            SELECT pg_catalog.pg_get_userbyid(d.datdba)
            FROM pg_catalog.pg_database d
            WHERE d.datname = current_database()
      );

      --RAISE NOTICE 'Record for event trigger %, objid: %,tag: %, current_user: %, database_owner: %, schemaname: %', r.object_identity, r.objid, tg_tag, current_user, databaseowner, r.schema_name;

      IF r.object_identity = 'postgis_topology' THEN
          EXECUTE format('DROP SCHEMA IF EXISTS topology');
      END IF;
    END LOOP;

  END IF;
END;
$$;
 "   DROP FUNCTION _heroku.drop_ext();
       _heroku          heroku_admin    false    7            `           1255    26133081    extension_before_drop()    FUNCTION     �  CREATE FUNCTION _heroku.extension_before_drop() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  query TEXT;

BEGIN
  query = (SELECT current_query());

  -- RAISE NOTICE 'executing extension_before_drop: tg_event: %, tg_tag: %, current_user: %, session_user: %, query: %', tg_event, tg_tag, current_user, session_user, query;
  IF tg_tag = 'DROP EXTENSION' and not pg_has_role(session_user, 'rds_superuser', 'MEMBER') THEN
    -- DROP EXTENSION [ IF EXISTS ] name [, ...] [ CASCADE | RESTRICT ]
    IF (regexp_match(query, 'DROP\s+EXTENSION\s+(IF\s+EXISTS)?.*(plpgsql)', 'i') IS NOT NULL) THEN
      RAISE EXCEPTION 'The plpgsql extension is required for database management and cannot be dropped.';
    END IF;
  END IF;
END;
$$;
 /   DROP FUNCTION _heroku.extension_before_drop();
       _heroku          heroku_admin    false    7            a           1255    26133082    postgis_after_create()    FUNCTION        CREATE FUNCTION _heroku.postgis_after_create() RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    schemaname TEXT;
    databaseowner TEXT;
BEGIN
    schemaname = (
        SELECT n.nspname
        FROM pg_catalog.pg_extension AS e
        INNER JOIN pg_catalog.pg_namespace AS n ON e.extnamespace = n.oid
        WHERE e.extname = 'postgis'
    );
    databaseowner = (
        SELECT pg_catalog.pg_get_userbyid(d.datdba)
        FROM pg_catalog.pg_database d
        WHERE d.datname = current_database()
    );

    EXECUTE format('GRANT EXECUTE ON FUNCTION %I.st_tileenvelope TO %I;', schemaname, databaseowner);
    EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.spatial_ref_sys TO %I;', schemaname, databaseowner);
END;
$$;
 .   DROP FUNCTION _heroku.postgis_after_create();
       _heroku          heroku_admin    false    7            b           1255    26133083    validate_extension()    FUNCTION       CREATE FUNCTION _heroku.validate_extension() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  r RECORD;

BEGIN

  IF tg_tag = 'CREATE EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
      CONTINUE WHEN r.command_tag != 'CREATE EXTENSION' OR r.object_type != 'extension';

      schemaname = (
        SELECT n.nspname
        FROM pg_catalog.pg_extension AS e
        INNER JOIN pg_catalog.pg_namespace AS n
        ON e.extnamespace = n.oid
        WHERE e.oid = r.objid
      );

      IF schemaname = '_heroku' THEN
        RAISE EXCEPTION 'Creating extensions in the _heroku schema is not allowed';
      END IF;
    END LOOP;
  END IF;
END;
$$;
 ,   DROP FUNCTION _heroku.validate_extension();
       _heroku          heroku_admin    false    7            m           0    0 G   FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint)    ACL     o   GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint) TO u2m65eq7rc7j8s;
          public          rdsadmin    false    368            �            1259    26133300    account_emailaddress    TABLE     �   CREATE TABLE public.account_emailaddress (
    id integer NOT NULL,
    email character varying(254) NOT NULL,
    verified boolean NOT NULL,
    "primary" boolean NOT NULL,
    user_id bigint NOT NULL
);
 (   DROP TABLE public.account_emailaddress;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133299    account_emailaddress_id_seq    SEQUENCE     �   ALTER TABLE public.account_emailaddress ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.account_emailaddress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    236            �            1259    26133308    account_emailconfirmation    TABLE     �   CREATE TABLE public.account_emailconfirmation (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    sent timestamp with time zone,
    key character varying(64) NOT NULL,
    email_address_id integer NOT NULL
);
 -   DROP TABLE public.account_emailconfirmation;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133307     account_emailconfirmation_id_seq    SEQUENCE     �   ALTER TABLE public.account_emailconfirmation ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.account_emailconfirmation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    238            �            1259    26133359    asseessments_assessment    TABLE        CREATE TABLE public.asseessments_assessment (
    id bigint NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    duration integer NOT NULL,
    CONSTRAINT asseessments_assessment_duration_check CHECK ((duration >= 0))
);
 +   DROP TABLE public.asseessments_assessment;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133358    asseessments_assessment_id_seq    SEQUENCE     �   ALTER TABLE public.asseessments_assessment ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.asseessments_assessment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    242    6            �            1259    26133368    asseessments_option    TABLE     �   CREATE TABLE public.asseessments_option (
    id bigint NOT NULL,
    option_text character varying(255) NOT NULL,
    is_correct boolean NOT NULL,
    question_id bigint NOT NULL
);
 '   DROP TABLE public.asseessments_option;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133367    asseessments_option_id_seq    SEQUENCE     �   ALTER TABLE public.asseessments_option ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.asseessments_option_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    244    6            �            1259    26133374    asseessments_question    TABLE     �   CREATE TABLE public.asseessments_question (
    id bigint NOT NULL,
    question_text text NOT NULL,
    assessment_id bigint NOT NULL
);
 )   DROP TABLE public.asseessments_question;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133373    asseessments_question_id_seq    SEQUENCE     �   ALTER TABLE public.asseessments_question ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.asseessments_question_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    246    6            �            1259    26133382    asseessments_result    TABLE     �   CREATE TABLE public.asseessments_result (
    id bigint NOT NULL,
    question_id bigint NOT NULL,
    selected_option_id bigint NOT NULL,
    session_id bigint NOT NULL
);
 '   DROP TABLE public.asseessments_result;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133381    asseessments_result_id_seq    SEQUENCE     �   ALTER TABLE public.asseessments_result ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.asseessments_result_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    248            �            1259    26133388    asseessments_session    TABLE     �   CREATE TABLE public.asseessments_session (
    id bigint NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    assessment_id bigint NOT NULL,
    user_id bigint NOT NULL
);
 (   DROP TABLE public.asseessments_session;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133387    asseessments_session_id_seq    SEQUENCE     �   ALTER TABLE public.asseessments_session ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.asseessments_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    250            �            1259    26133206 
   auth_group    TABLE     f   CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);
    DROP TABLE public.auth_group;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133205    auth_group_id_seq    SEQUENCE     �   ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    226            �            1259    26133214    auth_group_permissions    TABLE     �   CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);
 *   DROP TABLE public.auth_group_permissions;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133213    auth_group_permissions_id_seq    SEQUENCE     �   ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    228            �            1259    26133200    auth_permission    TABLE     �   CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);
 #   DROP TABLE public.auth_permission;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133199    auth_permission_id_seq    SEQUENCE     �   ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    224    6            [           1259    28295563    cities_light_city    TABLE     6  CREATE TABLE public.cities_light_city (
    id integer NOT NULL,
    name_ascii character varying(200) NOT NULL,
    slug character varying(50) NOT NULL,
    geoname_id integer,
    alternate_names text,
    name character varying(200) NOT NULL,
    display_name character varying(200) NOT NULL,
    search_names text NOT NULL,
    latitude numeric(8,5),
    longitude numeric(8,5),
    region_id integer,
    country_id integer NOT NULL,
    population bigint,
    feature_code character varying(10),
    timezone character varying(40),
    subregion_id integer
);
 %   DROP TABLE public.cities_light_city;
       public         heap    u2m65eq7rc7j8s    false    6            Z           1259    28295562    cities_light_city_id_seq    SEQUENCE     �   ALTER TABLE public.cities_light_city ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.cities_light_city_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    347            W           1259    28295506    cities_light_country    TABLE     �  CREATE TABLE public.cities_light_country (
    id integer NOT NULL,
    name_ascii character varying(200) NOT NULL,
    slug character varying(50) NOT NULL,
    geoname_id integer,
    alternate_names text,
    name character varying(200) NOT NULL,
    code2 character varying(2),
    code3 character varying(3),
    continent character varying(2) NOT NULL,
    tld character varying(5) NOT NULL,
    phone character varying(20)
);
 (   DROP TABLE public.cities_light_country;
       public         heap    u2m65eq7rc7j8s    false    6            V           1259    28295505    cities_light_country_id_seq    SEQUENCE     �   ALTER TABLE public.cities_light_country ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.cities_light_country_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    343    6            Y           1259    28295522    cities_light_region    TABLE     u  CREATE TABLE public.cities_light_region (
    id integer NOT NULL,
    name_ascii character varying(200) NOT NULL,
    slug character varying(50) NOT NULL,
    geoname_id integer,
    alternate_names text,
    name character varying(200) NOT NULL,
    display_name character varying(200) NOT NULL,
    geoname_code character varying(50),
    country_id integer NOT NULL
);
 '   DROP TABLE public.cities_light_region;
       public         heap    u2m65eq7rc7j8s    false    6            X           1259    28295521    cities_light_region_id_seq    SEQUENCE     �   ALTER TABLE public.cities_light_region ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.cities_light_region_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    345            ]           1259    28295601    cities_light_subregion    TABLE     �  CREATE TABLE public.cities_light_subregion (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    name_ascii character varying(200) NOT NULL,
    slug character varying(50) NOT NULL,
    geoname_id integer,
    alternate_names text,
    display_name character varying(200) NOT NULL,
    geoname_code character varying(50),
    country_id integer NOT NULL,
    region_id integer
);
 *   DROP TABLE public.cities_light_subregion;
       public         heap    u2m65eq7rc7j8s    false    6            \           1259    28295600    cities_light_subregion_id_seq    SEQUENCE     �   ALTER TABLE public.cities_light_subregion ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.cities_light_subregion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    349            �            1259    26133436    company_company    TABLE     �  CREATE TABLE public.company_company (
    id integer NOT NULL,
    name character varying(100),
    logo character varying(100) NOT NULL,
    founded integer,
    location character varying(100),
    user_id bigint NOT NULL,
    description text,
    contact_email character varying(254),
    contact_phone character varying(20),
    cover_photo character varying(100) NOT NULL,
    facebook character varying(200),
    industry character varying(50),
    instagram character varying(200),
    job_openings text,
    linkedin character varying(200),
    mission_statement text,
    size character varying(50),
    twitter character varying(200),
    video_introduction character varying(200),
    vision_statement text,
    website_url character varying(200),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    country character varying(2) NOT NULL,
    CONSTRAINT company_company_founded_12dd5f57_check CHECK ((founded >= 0))
);
 #   DROP TABLE public.company_company;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133435    company_company_id_seq    SEQUENCE     �   ALTER TABLE public.company_company ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.company_company_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    252    6            �            1259    26133337    django_admin_log    TABLE     �  CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);
 $   DROP TABLE public.django_admin_log;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133336    django_admin_log_id_seq    SEQUENCE     �   ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    240            �            1259    26133192    django_content_type    TABLE     �   CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);
 '   DROP TABLE public.django_content_type;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133191    django_content_type_id_seq    SEQUENCE     �   ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    222            �            1259    26133184    django_migrations    TABLE     �   CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);
 %   DROP TABLE public.django_migrations;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133183    django_migrations_id_seq    SEQUENCE     �   ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    220    6            7           1259    26134151    django_session    TABLE     �   CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);
 "   DROP TABLE public.django_session;
       public         heap    u2m65eq7rc7j8s    false    6            9           1259    26134161    django_site    TABLE     �   CREATE TABLE public.django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);
    DROP TABLE public.django_site;
       public         heap    u2m65eq7rc7j8s    false    6            8           1259    26134160    django_site_id_seq    SEQUENCE     �   ALTER TABLE public.django_site ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    313    6                       1259    26133741    job_applicantanswer    TABLE       CREATE TABLE public.job_applicantanswer (
    id bigint NOT NULL,
    answer character varying(255) NOT NULL,
    score integer NOT NULL,
    applicant_id bigint NOT NULL,
    job_id bigint NOT NULL,
    question_id bigint NOT NULL,
    application_id bigint NOT NULL
);
 '   DROP TABLE public.job_applicantanswer;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133740    job_applicantanswer_id_seq    SEQUENCE     �   ALTER TABLE public.job_applicantanswer ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_applicantanswer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    276    6                       1259    26133747    job_application    TABLE     �  CREATE TABLE public.job_application (
    id bigint NOT NULL,
    quiz_score integer NOT NULL,
    matching_percentage double precision NOT NULL,
    overall_match_percentage double precision NOT NULL,
    has_completed_quiz boolean NOT NULL,
    job_id bigint NOT NULL,
    user_id bigint NOT NULL,
    round_scores jsonb NOT NULL,
    total_scores jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
 #   DROP TABLE public.job_application;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133746    job_application_id_seq    SEQUENCE     �   ALTER TABLE public.job_application ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_application_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    278    6            $           1259    26133904    job_completedskills    TABLE     �   CREATE TABLE public.job_completedskills (
    id bigint NOT NULL,
    is_completed boolean NOT NULL,
    completed_at timestamp with time zone NOT NULL,
    job_id bigint,
    skill_id bigint,
    user_id bigint NOT NULL
);
 '   DROP TABLE public.job_completedskills;
       public         heap    u2m65eq7rc7j8s    false    6            #           1259    26133903    job_completedskills_id_seq    SEQUENCE     �   ALTER TABLE public.job_completedskills ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_completedskills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    292    6                       1259    26133753    job_job    TABLE     �  CREATE TABLE public.job_job (
    id bigint NOT NULL,
    title character varying(100) NOT NULL,
    location character varying(100) NOT NULL,
    salary bigint NOT NULL,
    ideal_candidate text NOT NULL,
    is_available boolean NOT NULL,
    description text NOT NULL,
    responsibilities text NOT NULL,
    benefits text NOT NULL,
    level character varying(10) NOT NULL,
    category_id bigint NOT NULL,
    company_id integer NOT NULL,
    user_id bigint NOT NULL,
    hire_number integer NOT NULL,
    job_type character varying(255) NOT NULL,
    experience_levels character varying(255) NOT NULL,
    job_location_type character varying(50) NOT NULL,
    shifts character varying(255) NOT NULL,
    weekly_ranges character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT job_job_salary_check CHECK ((salary >= 0))
);
    DROP TABLE public.job_job;
       public         heap    u2m65eq7rc7j8s    false    6                        1259    26133817    job_job_extracted_skills    TABLE     �   CREATE TABLE public.job_job_extracted_skills (
    id bigint NOT NULL,
    job_id bigint NOT NULL,
    skill_id bigint NOT NULL
);
 ,   DROP TABLE public.job_job_extracted_skills;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133816    job_job_extracted_skills_id_seq    SEQUENCE     �   ALTER TABLE public.job_job_extracted_skills ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_job_extracted_skills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    288                       1259    26133752    job_job_id_seq    SEQUENCE     �   ALTER TABLE public.job_job ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_job_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    280            "           1259    26133823    job_job_requirements    TABLE        CREATE TABLE public.job_job_requirements (
    id bigint NOT NULL,
    job_id bigint NOT NULL,
    skill_id bigint NOT NULL
);
 (   DROP TABLE public.job_job_requirements;
       public         heap    u2m65eq7rc7j8s    false    6            !           1259    26133822    job_job_requirements_id_seq    SEQUENCE     �   ALTER TABLE public.job_job_requirements ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_job_requirements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    290                       1259    26133762    job_mcq    TABLE     r  CREATE TABLE public.job_mcq (
    id bigint NOT NULL,
    question character varying(255) NOT NULL,
    option_a character varying(100) NOT NULL,
    option_b character varying(100) NOT NULL,
    option_c character varying(100) NOT NULL,
    option_d character varying(100) NOT NULL,
    correct_answer character varying(1) NOT NULL,
    job_title_id bigint NOT NULL
);
    DROP TABLE public.job_mcq;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133761    job_mcq_id_seq    SEQUENCE     �   ALTER TABLE public.job_mcq ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_mcq_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    282    6                       1259    26133770    job_savedjob    TABLE     �   CREATE TABLE public.job_savedjob (
    id bigint NOT NULL,
    saved_at timestamp with time zone NOT NULL,
    job_id bigint NOT NULL,
    user_id bigint NOT NULL
);
     DROP TABLE public.job_savedjob;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133769    job_savedjob_id_seq    SEQUENCE     �   ALTER TABLE public.job_savedjob ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_savedjob_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    284    6                       1259    26133776    job_skillquestion    TABLE     �  CREATE TABLE public.job_skillquestion (
    id bigint NOT NULL,
    question character varying(255) NOT NULL,
    option_a character varying(100) NOT NULL,
    option_b character varying(100) NOT NULL,
    option_c character varying(100) NOT NULL,
    option_d character varying(100) NOT NULL,
    correct_answer character varying(1) NOT NULL,
    entry_level character varying(100),
    skill_id bigint NOT NULL,
    job_id bigint
);
 %   DROP TABLE public.job_skillquestion;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133775    job_skillquestion_id_seq    SEQUENCE     �   ALTER TABLE public.job_skillquestion ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.job_skillquestion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    286    6            (           1259    26133968    messaging_chatmessage    TABLE     �   CREATE TABLE public.messaging_chatmessage (
    id bigint NOT NULL,
    text text NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    conversation_id bigint NOT NULL,
    sender_id bigint NOT NULL
);
 )   DROP TABLE public.messaging_chatmessage;
       public         heap    u2m65eq7rc7j8s    false    6            '           1259    26133967    messaging_chatmessage_id_seq    SEQUENCE     �   ALTER TABLE public.messaging_chatmessage ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.messaging_chatmessage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    296            &           1259    26133962    messaging_conversation    TABLE     �   CREATE TABLE public.messaging_conversation (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    participant1_id bigint NOT NULL,
    participant2_id bigint NOT NULL
);
 *   DROP TABLE public.messaging_conversation;
       public         heap    u2m65eq7rc7j8s    false    6            %           1259    26133961    messaging_conversation_id_seq    SEQUENCE     �   ALTER TABLE public.messaging_conversation ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.messaging_conversation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    294    6            *           1259    26134001    notifications_notification    TABLE     �   CREATE TABLE public.notifications_notification (
    id bigint NOT NULL,
    message text NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    is_read boolean NOT NULL,
    user_id bigint NOT NULL
);
 .   DROP TABLE public.notifications_notification;
       public         heap    u2m65eq7rc7j8s    false    6            )           1259    26134000 !   notifications_notification_id_seq    SEQUENCE     �   ALTER TABLE public.notifications_notification ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.notifications_notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    298    6            ,           1259    26134015 !   onboarding_generalknowledgeanswer    TABLE     �   CREATE TABLE public.onboarding_generalknowledgeanswer (
    id bigint NOT NULL,
    answer character varying(100) NOT NULL,
    is_correct boolean NOT NULL,
    question_id bigint NOT NULL
);
 5   DROP TABLE public.onboarding_generalknowledgeanswer;
       public         heap    u2m65eq7rc7j8s    false    6            +           1259    26134014 (   onboarding_generalknowledgeanswer_id_seq    SEQUENCE       ALTER TABLE public.onboarding_generalknowledgeanswer ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.onboarding_generalknowledgeanswer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    300            .           1259    26134021 #   onboarding_generalknowledgequestion    TABLE     �   CREATE TABLE public.onboarding_generalknowledgequestion (
    id bigint NOT NULL,
    question character varying(200) NOT NULL
);
 7   DROP TABLE public.onboarding_generalknowledgequestion;
       public         heap    u2m65eq7rc7j8s    false    6            -           1259    26134020 *   onboarding_generalknowledgequestion_id_seq    SEQUENCE       ALTER TABLE public.onboarding_generalknowledgequestion ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.onboarding_generalknowledgequestion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    302    6            0           1259    26134027    onboarding_quizresponse    TABLE     �   CREATE TABLE public.onboarding_quizresponse (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    answer_id bigint NOT NULL,
    application_id bigint NOT NULL,
    resume_id integer NOT NULL
);
 +   DROP TABLE public.onboarding_quizresponse;
       public         heap    u2m65eq7rc7j8s    false    6            /           1259    26134026    onboarding_quizresponse_id_seq    SEQUENCE     �   ALTER TABLE public.onboarding_quizresponse ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.onboarding_quizresponse_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    304                       1259    26133695    resume_contactinfo    TABLE     #  CREATE TABLE public.resume_contactinfo (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(254) NOT NULL,
    phone character varying(20) NOT NULL,
    user_id bigint NOT NULL,
    country character varying(2) NOT NULL,
    job_title_id bigint
);
 &   DROP TABLE public.resume_contactinfo;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133694    resume_contactinfo_id_seq    SEQUENCE     �   ALTER TABLE public.resume_contactinfo ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_contactinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    274            �            1259    26133465    resume_education    TABLE     (  CREATE TABLE public.resume_education (
    id bigint NOT NULL,
    institution_name character varying(100) NOT NULL,
    degree character varying(100) NOT NULL,
    graduation_year integer NOT NULL,
    resume_id integer,
    user_id bigint NOT NULL,
    field_of_study character varying(255)
);
 $   DROP TABLE public.resume_education;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133464    resume_education_id_seq    SEQUENCE     �   ALTER TABLE public.resume_education ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_education_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    254    6                        1259    26133471    resume_experience    TABLE     �   CREATE TABLE public.resume_experience (
    id bigint NOT NULL,
    company_name character varying(100) NOT NULL,
    role character varying(100) NOT NULL,
    resume_id integer,
    user_id bigint NOT NULL,
    end_date date,
    start_date date
);
 %   DROP TABLE public.resume_experience;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133470    resume_experience_id_seq    SEQUENCE     �   ALTER TABLE public.resume_experience ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_experience_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    256            4           1259    26134085    resume_language    TABLE     j   CREATE TABLE public.resume_language (
    id bigint NOT NULL,
    name character varying(100) NOT NULL
);
 #   DROP TABLE public.resume_language;
       public         heap    u2m65eq7rc7j8s    false    6            3           1259    26134084    resume_language_id_seq    SEQUENCE     �   ALTER TABLE public.resume_language ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_language_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    308                       1259    26133477    resume_resume    TABLE     B  CREATE TABLE public.resume_resume (
    id integer NOT NULL,
    first_name character varying(100),
    surname character varying(100),
    state character varying(100),
    country character varying(100),
    job_title character varying(100),
    date_of_birth date,
    phone character varying(20),
    description text NOT NULL,
    profile_image character varying(100) NOT NULL,
    cv character varying(100) NOT NULL,
    user_id bigint NOT NULL,
    category_id bigint,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
 !   DROP TABLE public.resume_resume;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133476    resume_resume_id_seq    SEQUENCE     �   ALTER TABLE public.resume_resume ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_resume_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    258                       1259    26133558    resume_resume_skills    TABLE     �   CREATE TABLE public.resume_resume_skills (
    id bigint NOT NULL,
    resume_id integer NOT NULL,
    skill_id bigint NOT NULL
);
 (   DROP TABLE public.resume_resume_skills;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133557    resume_resume_skills_id_seq    SEQUENCE     �   ALTER TABLE public.resume_resume_skills ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_resume_skills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    270            
           1259    26133503    resume_resumedoc    TABLE     B  CREATE TABLE public.resume_resumedoc (
    id integer NOT NULL,
    file character varying(100) NOT NULL,
    extracted_text text NOT NULL,
    uploaded_at timestamp with time zone NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
 $   DROP TABLE public.resume_resumedoc;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133511 !   resume_resumedoc_extracted_skills    TABLE     �   CREATE TABLE public.resume_resumedoc_extracted_skills (
    id bigint NOT NULL,
    resumedoc_id integer NOT NULL,
    skill_id bigint NOT NULL
);
 5   DROP TABLE public.resume_resumedoc_extracted_skills;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133510 (   resume_resumedoc_extracted_skills_id_seq    SEQUENCE       ALTER TABLE public.resume_resumedoc_extracted_skills ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_resumedoc_extracted_skills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    268    6            	           1259    26133502    resume_resumedoc_id_seq    SEQUENCE     �   ALTER TABLE public.resume_resumedoc ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_resumedoc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    266    6                       1259    26133491    resume_skill    TABLE     �   CREATE TABLE public.resume_skill (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    is_extracted boolean NOT NULL,
    user_id bigint NOT NULL
);
     DROP TABLE public.resume_skill;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133497    resume_skill_categories    TABLE     �   CREATE TABLE public.resume_skill_categories (
    id bigint NOT NULL,
    skill_id bigint NOT NULL,
    skillcategory_id bigint NOT NULL
);
 +   DROP TABLE public.resume_skill_categories;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133496    resume_skill_categories_id_seq    SEQUENCE     �   ALTER TABLE public.resume_skill_categories ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_skill_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    264    6                       1259    26133490    resume_skill_id_seq    SEQUENCE     �   ALTER TABLE public.resume_skill ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_skill_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    262    6                       1259    26133485    resume_skillcategory    TABLE     o   CREATE TABLE public.resume_skillcategory (
    id bigint NOT NULL,
    name character varying(100) NOT NULL
);
 (   DROP TABLE public.resume_skillcategory;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133484    resume_skillcategory_id_seq    SEQUENCE     �   ALTER TABLE public.resume_skillcategory ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_skillcategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    260            6           1259    26134116    resume_userlanguage    TABLE     �   CREATE TABLE public.resume_userlanguage (
    id bigint NOT NULL,
    language_id bigint NOT NULL,
    user_profile_id bigint NOT NULL
);
 '   DROP TABLE public.resume_userlanguage;
       public         heap    u2m65eq7rc7j8s    false    6            5           1259    26134115    resume_userlanguage_id_seq    SEQUENCE     �   ALTER TABLE public.resume_userlanguage ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_userlanguage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    310    6            2           1259    26134072    resume_userprofile    TABLE     �   CREATE TABLE public.resume_userprofile (
    id bigint NOT NULL,
    country character varying(2) NOT NULL,
    user_id bigint NOT NULL
);
 &   DROP TABLE public.resume_userprofile;
       public         heap    u2m65eq7rc7j8s    false    6            1           1259    26134071    resume_userprofile_id_seq    SEQUENCE     �   ALTER TABLE public.resume_userprofile ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_userprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    306                       1259    26133689    resume_workexperience    TABLE     �   CREATE TABLE public.resume_workexperience (
    id bigint NOT NULL,
    company_name character varying(100) NOT NULL,
    role character varying(100) NOT NULL,
    user_id bigint NOT NULL,
    end_date date,
    resume_id integer,
    start_date date
);
 )   DROP TABLE public.resume_workexperience;
       public         heap    u2m65eq7rc7j8s    false    6                       1259    26133688    resume_workexperience_id_seq    SEQUENCE     �   ALTER TABLE public.resume_workexperience ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.resume_workexperience_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    272    6            ;           1259    26134170    social_auth_association    TABLE     ;  CREATE TABLE public.social_auth_association (
    id bigint NOT NULL,
    server_url character varying(255) NOT NULL,
    handle character varying(255) NOT NULL,
    secret character varying(255) NOT NULL,
    issued integer NOT NULL,
    lifetime integer NOT NULL,
    assoc_type character varying(64) NOT NULL
);
 +   DROP TABLE public.social_auth_association;
       public         heap    u2m65eq7rc7j8s    false    6            :           1259    26134169    social_auth_association_id_seq    SEQUENCE     �   ALTER TABLE public.social_auth_association ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_auth_association_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    315            =           1259    26134178    social_auth_code    TABLE     �   CREATE TABLE public.social_auth_code (
    id bigint NOT NULL,
    email character varying(254) NOT NULL,
    code character varying(32) NOT NULL,
    verified boolean NOT NULL,
    "timestamp" timestamp with time zone NOT NULL
);
 $   DROP TABLE public.social_auth_code;
       public         heap    u2m65eq7rc7j8s    false    6            <           1259    26134177    social_auth_code_id_seq    SEQUENCE     �   ALTER TABLE public.social_auth_code ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_auth_code_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    317    6            ?           1259    26134184    social_auth_nonce    TABLE     �   CREATE TABLE public.social_auth_nonce (
    id bigint NOT NULL,
    server_url character varying(255) NOT NULL,
    "timestamp" integer NOT NULL,
    salt character varying(65) NOT NULL
);
 %   DROP TABLE public.social_auth_nonce;
       public         heap    u2m65eq7rc7j8s    false    6            >           1259    26134183    social_auth_nonce_id_seq    SEQUENCE     �   ALTER TABLE public.social_auth_nonce ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_auth_nonce_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    319            C           1259    26134217    social_auth_partial    TABLE     T  CREATE TABLE public.social_auth_partial (
    id bigint NOT NULL,
    token character varying(32) NOT NULL,
    next_step smallint NOT NULL,
    backend character varying(32) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    data jsonb NOT NULL,
    CONSTRAINT social_auth_partial_next_step_check CHECK ((next_step >= 0))
);
 '   DROP TABLE public.social_auth_partial;
       public         heap    u2m65eq7rc7j8s    false    6            B           1259    26134216    social_auth_partial_id_seq    SEQUENCE     �   ALTER TABLE public.social_auth_partial ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_auth_partial_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    323    6            A           1259    26134190    social_auth_usersocialauth    TABLE     <  CREATE TABLE public.social_auth_usersocialauth (
    id bigint NOT NULL,
    provider character varying(32) NOT NULL,
    uid character varying(255) NOT NULL,
    user_id bigint NOT NULL,
    created timestamp with time zone NOT NULL,
    modified timestamp with time zone NOT NULL,
    extra_data jsonb NOT NULL
);
 .   DROP TABLE public.social_auth_usersocialauth;
       public         heap    u2m65eq7rc7j8s    false    6            @           1259    26134189 !   social_auth_usersocialauth_id_seq    SEQUENCE     �   ALTER TABLE public.social_auth_usersocialauth ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_auth_usersocialauth_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    321            M           1259    26134357    social_features_comment    TABLE     �   CREATE TABLE public.social_features_comment (
    id bigint NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    post_id uuid NOT NULL,
    user_id bigint NOT NULL
);
 +   DROP TABLE public.social_features_comment;
       public         heap    u2m65eq7rc7j8s    false    6            L           1259    26134356    social_features_comment_id_seq    SEQUENCE     �   ALTER TABLE public.social_features_comment ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_features_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    333            K           1259    26134351    social_features_follow    TABLE     �   CREATE TABLE public.social_features_follow (
    id bigint NOT NULL,
    followed_id bigint NOT NULL,
    follower_id bigint NOT NULL
);
 *   DROP TABLE public.social_features_follow;
       public         heap    u2m65eq7rc7j8s    false    6            J           1259    26134350    social_features_follow_id_seq    SEQUENCE     �   ALTER TABLE public.social_features_follow ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_features_follow_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    331    6            I           1259    26134345    social_features_like    TABLE     }   CREATE TABLE public.social_features_like (
    id bigint NOT NULL,
    post_id uuid NOT NULL,
    user_id bigint NOT NULL
);
 (   DROP TABLE public.social_features_like;
       public         heap    u2m65eq7rc7j8s    false    6            H           1259    26134344    social_features_like_id_seq    SEQUENCE     �   ALTER TABLE public.social_features_like ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_features_like_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    329            E           1259    26134303    social_features_message    TABLE     �   CREATE TABLE public.social_features_message (
    id uuid NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    is_read boolean NOT NULL,
    recipient_id bigint NOT NULL,
    sender_id bigint NOT NULL
);
 +   DROP TABLE public.social_features_message;
       public         heap    u2m65eq7rc7j8s    false    6            D           1259    26134296    social_features_post    TABLE     �   CREATE TABLE public.social_features_post (
    id uuid NOT NULL,
    content text NOT NULL,
    image character varying(100),
    created_at timestamp with time zone NOT NULL,
    author_id bigint NOT NULL
);
 (   DROP TABLE public.social_features_post;
       public         heap    u2m65eq7rc7j8s    false    6            G           1259    26134335    social_features_userprofile    TABLE     �   CREATE TABLE public.social_features_userprofile (
    id bigint NOT NULL,
    bio text NOT NULL,
    profile_picture character varying(100),
    user_id bigint NOT NULL
);
 /   DROP TABLE public.social_features_userprofile;
       public         heap    u2m65eq7rc7j8s    false    6            F           1259    26134334 "   social_features_userprofile_id_seq    SEQUENCE     �   ALTER TABLE public.social_features_userprofile ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.social_features_userprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    327    6            O           1259    26134407    socialaccount_socialaccount    TABLE     E  CREATE TABLE public.socialaccount_socialaccount (
    id integer NOT NULL,
    provider character varying(200) NOT NULL,
    uid character varying(191) NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    extra_data jsonb NOT NULL,
    user_id bigint NOT NULL
);
 /   DROP TABLE public.socialaccount_socialaccount;
       public         heap    u2m65eq7rc7j8s    false    6            N           1259    26134406 "   socialaccount_socialaccount_id_seq    SEQUENCE     �   ALTER TABLE public.socialaccount_socialaccount ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.socialaccount_socialaccount_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    335            Q           1259    26134415    socialaccount_socialapp    TABLE     q  CREATE TABLE public.socialaccount_socialapp (
    id integer NOT NULL,
    provider character varying(30) NOT NULL,
    name character varying(40) NOT NULL,
    client_id character varying(191) NOT NULL,
    secret character varying(191) NOT NULL,
    key character varying(191) NOT NULL,
    provider_id character varying(200) NOT NULL,
    settings jsonb NOT NULL
);
 +   DROP TABLE public.socialaccount_socialapp;
       public         heap    u2m65eq7rc7j8s    false    6            P           1259    26134414    socialaccount_socialapp_id_seq    SEQUENCE     �   ALTER TABLE public.socialaccount_socialapp ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.socialaccount_socialapp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    337            S           1259    26134421    socialaccount_socialapp_sites    TABLE     �   CREATE TABLE public.socialaccount_socialapp_sites (
    id bigint NOT NULL,
    socialapp_id integer NOT NULL,
    site_id integer NOT NULL
);
 1   DROP TABLE public.socialaccount_socialapp_sites;
       public         heap    u2m65eq7rc7j8s    false    6            R           1259    26134420 $   socialaccount_socialapp_sites_id_seq    SEQUENCE     �   ALTER TABLE public.socialaccount_socialapp_sites ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.socialaccount_socialapp_sites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    339            U           1259    26134427    socialaccount_socialtoken    TABLE     �   CREATE TABLE public.socialaccount_socialtoken (
    id integer NOT NULL,
    token text NOT NULL,
    token_secret text NOT NULL,
    expires_at timestamp with time zone,
    account_id integer NOT NULL,
    app_id integer
);
 -   DROP TABLE public.socialaccount_socialtoken;
       public         heap    u2m65eq7rc7j8s    false    6            T           1259    26134426     socialaccount_socialtoken_id_seq    SEQUENCE     �   ALTER TABLE public.socialaccount_socialtoken ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.socialaccount_socialtoken_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    341            �            1259    26133246 
   users_user    TABLE     �  CREATE TABLE public.users_user (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(254) NOT NULL,
    is_recruiter boolean NOT NULL,
    is_applicant boolean NOT NULL,
    has_resume boolean NOT NULL,
    has_company boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
    DROP TABLE public.users_user;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133258    users_user_groups    TABLE     ~   CREATE TABLE public.users_user_groups (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    group_id integer NOT NULL
);
 %   DROP TABLE public.users_user_groups;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133257    users_user_groups_id_seq    SEQUENCE     �   ALTER TABLE public.users_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    232            �            1259    26133245    users_user_id_seq    SEQUENCE     �   ALTER TABLE public.users_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    230            �            1259    26133264    users_user_user_permissions    TABLE     �   CREATE TABLE public.users_user_user_permissions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission_id integer NOT NULL
);
 /   DROP TABLE public.users_user_user_permissions;
       public         heap    u2m65eq7rc7j8s    false    6            �            1259    26133263 "   users_user_user_permissions_id_seq    SEQUENCE     �   ALTER TABLE public.users_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          u2m65eq7rc7j8s    false    6    234            �          0    26133300    account_emailaddress 
   TABLE DATA           W   COPY public.account_emailaddress (id, email, verified, "primary", user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    236   ��      �          0    26133308    account_emailconfirmation 
   TABLE DATA           ]   COPY public.account_emailconfirmation (id, created, sent, key, email_address_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    238   J�      �          0    26133359    asseessments_assessment 
   TABLE DATA           S   COPY public.asseessments_assessment (id, title, description, duration) FROM stdin;
    public          u2m65eq7rc7j8s    false    242   g�      �          0    26133368    asseessments_option 
   TABLE DATA           W   COPY public.asseessments_option (id, option_text, is_correct, question_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    244   ��      �          0    26133374    asseessments_question 
   TABLE DATA           Q   COPY public.asseessments_question (id, question_text, assessment_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    246   ��      �          0    26133382    asseessments_result 
   TABLE DATA           ^   COPY public.asseessments_result (id, question_id, selected_option_id, session_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    248   ��      �          0    26133388    asseessments_session 
   TABLE DATA           `   COPY public.asseessments_session (id, start_time, end_time, assessment_id, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    250   ��      �          0    26133206 
   auth_group 
   TABLE DATA           .   COPY public.auth_group (id, name) FROM stdin;
    public          u2m65eq7rc7j8s    false    226   ��      �          0    26133214    auth_group_permissions 
   TABLE DATA           M   COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    228   �      �          0    26133200    auth_permission 
   TABLE DATA           N   COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
    public          u2m65eq7rc7j8s    false    224   2�      `          0    28295563    cities_light_city 
   TABLE DATA           �   COPY public.cities_light_city (id, name_ascii, slug, geoname_id, alternate_names, name, display_name, search_names, latitude, longitude, region_id, country_id, population, feature_code, timezone, subregion_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    347   ��      \          0    28295506    cities_light_country 
   TABLE DATA           �   COPY public.cities_light_country (id, name_ascii, slug, geoname_id, alternate_names, name, code2, code3, continent, tld, phone) FROM stdin;
    public          u2m65eq7rc7j8s    false    343   ��      ^          0    28295522    cities_light_region 
   TABLE DATA           �   COPY public.cities_light_region (id, name_ascii, slug, geoname_id, alternate_names, name, display_name, geoname_code, country_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    345   �      b          0    28295601    cities_light_subregion 
   TABLE DATA           �   COPY public.cities_light_subregion (id, name, name_ascii, slug, geoname_id, alternate_names, display_name, geoname_code, country_id, region_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    349   /�                0    26133436    company_company 
   TABLE DATA           :  COPY public.company_company (id, name, logo, founded, location, user_id, description, contact_email, contact_phone, cover_photo, facebook, industry, instagram, job_openings, linkedin, mission_statement, size, twitter, video_introduction, vision_statement, website_url, created_at, updated_at, country) FROM stdin;
    public          u2m65eq7rc7j8s    false    252   L�      �          0    26133337    django_admin_log 
   TABLE DATA           �   COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    240   �      �          0    26133192    django_content_type 
   TABLE DATA           C   COPY public.django_content_type (id, app_label, model) FROM stdin;
    public          u2m65eq7rc7j8s    false    222   ��      �          0    26133184    django_migrations 
   TABLE DATA           C   COPY public.django_migrations (id, app, name, applied) FROM stdin;
    public          u2m65eq7rc7j8s    false    220   �      <          0    26134151    django_session 
   TABLE DATA           P   COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
    public          u2m65eq7rc7j8s    false    311   ��      >          0    26134161    django_site 
   TABLE DATA           7   COPY public.django_site (id, domain, name) FROM stdin;
    public          u2m65eq7rc7j8s    false    313   l�                0    26133741    job_applicantanswer 
   TABLE DATA           s   COPY public.job_applicantanswer (id, answer, score, applicant_id, job_id, question_id, application_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    276   ��                0    26133747    job_application 
   TABLE DATA           �   COPY public.job_application (id, quiz_score, matching_percentage, overall_match_percentage, has_completed_quiz, job_id, user_id, round_scores, total_scores, created_at, updated_at) FROM stdin;
    public          u2m65eq7rc7j8s    false    278   ��      )          0    26133904    job_completedskills 
   TABLE DATA           h   COPY public.job_completedskills (id, is_completed, completed_at, job_id, skill_id, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    292   ��                0    26133753    job_job 
   TABLE DATA             COPY public.job_job (id, title, location, salary, ideal_candidate, is_available, description, responsibilities, benefits, level, category_id, company_id, user_id, hire_number, job_type, experience_levels, job_location_type, shifts, weekly_ranges, created_at, updated_at) FROM stdin;
    public          u2m65eq7rc7j8s    false    280   ��      %          0    26133817    job_job_extracted_skills 
   TABLE DATA           H   COPY public.job_job_extracted_skills (id, job_id, skill_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    288   ��      '          0    26133823    job_job_requirements 
   TABLE DATA           D   COPY public.job_job_requirements (id, job_id, skill_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    290   ��                0    26133762    job_mcq 
   TABLE DATA           u   COPY public.job_mcq (id, question, option_a, option_b, option_c, option_d, correct_answer, job_title_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    282   ,       !          0    26133770    job_savedjob 
   TABLE DATA           E   COPY public.job_savedjob (id, saved_at, job_id, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    284   I       #          0    26133776    job_skillquestion 
   TABLE DATA           �   COPY public.job_skillquestion (id, question, option_a, option_b, option_c, option_d, correct_answer, entry_level, skill_id, job_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    286   f       -          0    26133968    messaging_chatmessage 
   TABLE DATA           b   COPY public.messaging_chatmessage (id, text, "timestamp", conversation_id, sender_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    296   �      +          0    26133962    messaging_conversation 
   TABLE DATA           b   COPY public.messaging_conversation (id, created_at, participant1_id, participant2_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    294   �      /          0    26134001    notifications_notification 
   TABLE DATA           `   COPY public.notifications_notification (id, message, "timestamp", is_read, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    298   �      1          0    26134015 !   onboarding_generalknowledgeanswer 
   TABLE DATA           `   COPY public.onboarding_generalknowledgeanswer (id, answer, is_correct, question_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    300   �      3          0    26134021 #   onboarding_generalknowledgequestion 
   TABLE DATA           K   COPY public.onboarding_generalknowledgequestion (id, question) FROM stdin;
    public          u2m65eq7rc7j8s    false    302         5          0    26134027    onboarding_quizresponse 
   TABLE DATA           g   COPY public.onboarding_quizresponse (id, created_at, answer_id, application_id, resume_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    304   *                0    26133695    resume_contactinfo 
   TABLE DATA           d   COPY public.resume_contactinfo (id, name, email, phone, user_id, country, job_title_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    274   G                0    26133465    resume_education 
   TABLE DATA           }   COPY public.resume_education (id, institution_name, degree, graduation_year, resume_id, user_id, field_of_study) FROM stdin;
    public          u2m65eq7rc7j8s    false    254   �                0    26133471    resume_experience 
   TABLE DATA           m   COPY public.resume_experience (id, company_name, role, resume_id, user_id, end_date, start_date) FROM stdin;
    public          u2m65eq7rc7j8s    false    256   
      9          0    26134085    resume_language 
   TABLE DATA           3   COPY public.resume_language (id, name) FROM stdin;
    public          u2m65eq7rc7j8s    false    308   
                0    26133477    resume_resume 
   TABLE DATA           �   COPY public.resume_resume (id, first_name, surname, state, country, job_title, date_of_birth, phone, description, profile_image, cv, user_id, category_id, created_at, updated_at) FROM stdin;
    public          u2m65eq7rc7j8s    false    258   V
                0    26133558    resume_resume_skills 
   TABLE DATA           G   COPY public.resume_resume_skills (id, resume_id, skill_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    270   �                0    26133503    resume_resumedoc 
   TABLE DATA           r   COPY public.resume_resumedoc (id, file, extracted_text, uploaded_at, user_id, created_at, updated_at) FROM stdin;
    public          u2m65eq7rc7j8s    false    266   w                0    26133511 !   resume_resumedoc_extracted_skills 
   TABLE DATA           W   COPY public.resume_resumedoc_extracted_skills (id, resumedoc_id, skill_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    268   �                0    26133491    resume_skill 
   TABLE DATA           G   COPY public.resume_skill (id, name, is_extracted, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    262   �                0    26133497    resume_skill_categories 
   TABLE DATA           Q   COPY public.resume_skill_categories (id, skill_id, skillcategory_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    264   )      	          0    26133485    resume_skillcategory 
   TABLE DATA           8   COPY public.resume_skillcategory (id, name) FROM stdin;
    public          u2m65eq7rc7j8s    false    260   #      ;          0    26134116    resume_userlanguage 
   TABLE DATA           O   COPY public.resume_userlanguage (id, language_id, user_profile_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    310   �#      7          0    26134072    resume_userprofile 
   TABLE DATA           B   COPY public.resume_userprofile (id, country, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    306   �#                0    26133689    resume_workexperience 
   TABLE DATA           q   COPY public.resume_workexperience (id, company_name, role, user_id, end_date, resume_id, start_date) FROM stdin;
    public          u2m65eq7rc7j8s    false    272   �#      @          0    26134170    social_auth_association 
   TABLE DATA           o   COPY public.social_auth_association (id, server_url, handle, secret, issued, lifetime, assoc_type) FROM stdin;
    public          u2m65eq7rc7j8s    false    315   �$      B          0    26134178    social_auth_code 
   TABLE DATA           R   COPY public.social_auth_code (id, email, code, verified, "timestamp") FROM stdin;
    public          u2m65eq7rc7j8s    false    317   �$      D          0    26134184    social_auth_nonce 
   TABLE DATA           N   COPY public.social_auth_nonce (id, server_url, "timestamp", salt) FROM stdin;
    public          u2m65eq7rc7j8s    false    319   �$      H          0    26134217    social_auth_partial 
   TABLE DATA           _   COPY public.social_auth_partial (id, token, next_step, backend, "timestamp", data) FROM stdin;
    public          u2m65eq7rc7j8s    false    323   �$      F          0    26134190    social_auth_usersocialauth 
   TABLE DATA           o   COPY public.social_auth_usersocialauth (id, provider, uid, user_id, created, modified, extra_data) FROM stdin;
    public          u2m65eq7rc7j8s    false    321   %      R          0    26134357    social_features_comment 
   TABLE DATA           \   COPY public.social_features_comment (id, content, created_at, post_id, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    333   v&      P          0    26134351    social_features_follow 
   TABLE DATA           N   COPY public.social_features_follow (id, followed_id, follower_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    331   �&      N          0    26134345    social_features_like 
   TABLE DATA           D   COPY public.social_features_like (id, post_id, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    329   �&      J          0    26134303    social_features_message 
   TABLE DATA           l   COPY public.social_features_message (id, content, created_at, is_read, recipient_id, sender_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    325   �&      I          0    26134296    social_features_post 
   TABLE DATA           Y   COPY public.social_features_post (id, content, image, created_at, author_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    324   �&      L          0    26134335    social_features_userprofile 
   TABLE DATA           X   COPY public.social_features_userprofile (id, bio, profile_picture, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    327   '      T          0    26134407    socialaccount_socialaccount 
   TABLE DATA           v   COPY public.socialaccount_socialaccount (id, provider, uid, last_login, date_joined, extra_data, user_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    335   $'      V          0    26134415    socialaccount_socialapp 
   TABLE DATA           t   COPY public.socialaccount_socialapp (id, provider, name, client_id, secret, key, provider_id, settings) FROM stdin;
    public          u2m65eq7rc7j8s    false    337   A'      X          0    26134421    socialaccount_socialapp_sites 
   TABLE DATA           R   COPY public.socialaccount_socialapp_sites (id, socialapp_id, site_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    339   ^'      Z          0    26134427    socialaccount_socialtoken 
   TABLE DATA           l   COPY public.socialaccount_socialtoken (id, token, token_secret, expires_at, account_id, app_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    341   {'      �          0    26133246 
   users_user 
   TABLE DATA           �   COPY public.users_user (id, password, last_login, is_superuser, username, is_staff, is_active, date_joined, first_name, last_name, email, is_recruiter, is_applicant, has_resume, has_company, created_at, updated_at) FROM stdin;
    public          u2m65eq7rc7j8s    false    230   �'      �          0    26133258    users_user_groups 
   TABLE DATA           B   COPY public.users_user_groups (id, user_id, group_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    232   �*      �          0    26133264    users_user_user_permissions 
   TABLE DATA           Q   COPY public.users_user_user_permissions (id, user_id, permission_id) FROM stdin;
    public          u2m65eq7rc7j8s    false    234   �*      n           0    0    account_emailaddress_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.account_emailaddress_id_seq', 70, true);
          public          u2m65eq7rc7j8s    false    235            o           0    0     account_emailconfirmation_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.account_emailconfirmation_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    237            p           0    0    asseessments_assessment_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.asseessments_assessment_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    241            q           0    0    asseessments_option_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.asseessments_option_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    243            r           0    0    asseessments_question_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.asseessments_question_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    245            s           0    0    asseessments_result_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.asseessments_result_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    247            t           0    0    asseessments_session_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.asseessments_session_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    249            u           0    0    auth_group_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    225            v           0    0    auth_group_permissions_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    227            w           0    0    auth_permission_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.auth_permission_id_seq', 247, true);
          public          u2m65eq7rc7j8s    false    223            x           0    0    cities_light_city_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.cities_light_city_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    346            y           0    0    cities_light_country_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.cities_light_country_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    342            z           0    0    cities_light_region_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.cities_light_region_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    344            {           0    0    cities_light_subregion_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.cities_light_subregion_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    348            |           0    0    company_company_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.company_company_id_seq', 99, true);
          public          u2m65eq7rc7j8s    false    251            }           0    0    django_admin_log_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.django_admin_log_id_seq', 85, true);
          public          u2m65eq7rc7j8s    false    239            ~           0    0    django_content_type_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.django_content_type_id_seq', 70, true);
          public          u2m65eq7rc7j8s    false    221                       0    0    django_migrations_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.django_migrations_id_seq', 179, true);
          public          u2m65eq7rc7j8s    false    219            �           0    0    django_site_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.django_site_id_seq', 2, true);
          public          u2m65eq7rc7j8s    false    312            �           0    0    job_applicantanswer_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.job_applicantanswer_id_seq', 82, true);
          public          u2m65eq7rc7j8s    false    275            �           0    0    job_application_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.job_application_id_seq', 67, true);
          public          u2m65eq7rc7j8s    false    277            �           0    0    job_completedskills_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.job_completedskills_id_seq', 68, true);
          public          u2m65eq7rc7j8s    false    291            �           0    0    job_job_extracted_skills_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.job_job_extracted_skills_id_seq', 133, true);
          public          u2m65eq7rc7j8s    false    287            �           0    0    job_job_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.job_job_id_seq', 75, true);
          public          u2m65eq7rc7j8s    false    279            �           0    0    job_job_requirements_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.job_job_requirements_id_seq', 72, true);
          public          u2m65eq7rc7j8s    false    289            �           0    0    job_mcq_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.job_mcq_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    281            �           0    0    job_savedjob_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.job_savedjob_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    283            �           0    0    job_skillquestion_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.job_skillquestion_id_seq', 72, true);
          public          u2m65eq7rc7j8s    false    285            �           0    0    messaging_chatmessage_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.messaging_chatmessage_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    295            �           0    0    messaging_conversation_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.messaging_conversation_id_seq', 33, true);
          public          u2m65eq7rc7j8s    false    293            �           0    0 !   notifications_notification_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.notifications_notification_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    297            �           0    0 (   onboarding_generalknowledgeanswer_id_seq    SEQUENCE SET     W   SELECT pg_catalog.setval('public.onboarding_generalknowledgeanswer_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    299            �           0    0 *   onboarding_generalknowledgequestion_id_seq    SEQUENCE SET     Y   SELECT pg_catalog.setval('public.onboarding_generalknowledgequestion_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    301            �           0    0    onboarding_quizresponse_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.onboarding_quizresponse_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    303            �           0    0    resume_contactinfo_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.resume_contactinfo_id_seq', 67, true);
          public          u2m65eq7rc7j8s    false    273            �           0    0    resume_education_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.resume_education_id_seq', 72, true);
          public          u2m65eq7rc7j8s    false    253            �           0    0    resume_experience_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.resume_experience_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    255            �           0    0    resume_language_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.resume_language_id_seq', 3, true);
          public          u2m65eq7rc7j8s    false    307            �           0    0    resume_resume_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.resume_resume_id_seq', 70, true);
          public          u2m65eq7rc7j8s    false    257            �           0    0    resume_resume_skills_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.resume_resume_skills_id_seq', 2560, true);
          public          u2m65eq7rc7j8s    false    269            �           0    0 (   resume_resumedoc_extracted_skills_id_seq    SEQUENCE SET     X   SELECT pg_catalog.setval('public.resume_resumedoc_extracted_skills_id_seq', 220, true);
          public          u2m65eq7rc7j8s    false    267            �           0    0    resume_resumedoc_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.resume_resumedoc_id_seq', 67, true);
          public          u2m65eq7rc7j8s    false    265            �           0    0    resume_skill_categories_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.resume_skill_categories_id_seq', 298, true);
          public          u2m65eq7rc7j8s    false    263            �           0    0    resume_skill_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.resume_skill_id_seq', 282, true);
          public          u2m65eq7rc7j8s    false    261            �           0    0    resume_skillcategory_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.resume_skillcategory_id_seq', 69, true);
          public          u2m65eq7rc7j8s    false    259            �           0    0    resume_userlanguage_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.resume_userlanguage_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    309            �           0    0    resume_userprofile_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.resume_userprofile_id_seq', 67, true);
          public          u2m65eq7rc7j8s    false    305            �           0    0    resume_workexperience_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.resume_workexperience_id_seq', 70, true);
          public          u2m65eq7rc7j8s    false    271            �           0    0    social_auth_association_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.social_auth_association_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    314            �           0    0    social_auth_code_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.social_auth_code_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    316            �           0    0    social_auth_nonce_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.social_auth_nonce_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    318            �           0    0    social_auth_partial_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.social_auth_partial_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    322            �           0    0 !   social_auth_usersocialauth_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.social_auth_usersocialauth_id_seq', 34, true);
          public          u2m65eq7rc7j8s    false    320            �           0    0    social_features_comment_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.social_features_comment_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    332            �           0    0    social_features_follow_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.social_features_follow_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    330            �           0    0    social_features_like_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.social_features_like_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    328            �           0    0 "   social_features_userprofile_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.social_features_userprofile_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    326            �           0    0 "   socialaccount_socialaccount_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.socialaccount_socialaccount_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    334            �           0    0    socialaccount_socialapp_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.socialaccount_socialapp_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    336            �           0    0 $   socialaccount_socialapp_sites_id_seq    SEQUENCE SET     S   SELECT pg_catalog.setval('public.socialaccount_socialapp_sites_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    338            �           0    0     socialaccount_socialtoken_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.socialaccount_socialtoken_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    340            �           0    0    users_user_groups_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.users_user_groups_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    231            �           0    0    users_user_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.users_user_id_seq', 70, true);
          public          u2m65eq7rc7j8s    false    229            �           0    0 "   users_user_user_permissions_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.users_user_user_permissions_id_seq', 1, false);
          public          u2m65eq7rc7j8s    false    233            �           2606    26133304 .   account_emailaddress account_emailaddress_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.account_emailaddress
    ADD CONSTRAINT account_emailaddress_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.account_emailaddress DROP CONSTRAINT account_emailaddress_pkey;
       public            u2m65eq7rc7j8s    false    236            �           2606    26133333 E   account_emailaddress account_emailaddress_user_id_email_987c8728_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.account_emailaddress
    ADD CONSTRAINT account_emailaddress_user_id_email_987c8728_uniq UNIQUE (user_id, email);
 o   ALTER TABLE ONLY public.account_emailaddress DROP CONSTRAINT account_emailaddress_user_id_email_987c8728_uniq;
       public            u2m65eq7rc7j8s    false    236    236            �           2606    26133314 ;   account_emailconfirmation account_emailconfirmation_key_key 
   CONSTRAINT     u   ALTER TABLE ONLY public.account_emailconfirmation
    ADD CONSTRAINT account_emailconfirmation_key_key UNIQUE (key);
 e   ALTER TABLE ONLY public.account_emailconfirmation DROP CONSTRAINT account_emailconfirmation_key_key;
       public            u2m65eq7rc7j8s    false    238            �           2606    26133312 8   account_emailconfirmation account_emailconfirmation_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.account_emailconfirmation
    ADD CONSTRAINT account_emailconfirmation_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.account_emailconfirmation DROP CONSTRAINT account_emailconfirmation_pkey;
       public            u2m65eq7rc7j8s    false    238            �           2606    26133366 4   asseessments_assessment asseessments_assessment_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.asseessments_assessment
    ADD CONSTRAINT asseessments_assessment_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.asseessments_assessment DROP CONSTRAINT asseessments_assessment_pkey;
       public            u2m65eq7rc7j8s    false    242            �           2606    26133372 ,   asseessments_option asseessments_option_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.asseessments_option
    ADD CONSTRAINT asseessments_option_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.asseessments_option DROP CONSTRAINT asseessments_option_pkey;
       public            u2m65eq7rc7j8s    false    244            �           2606    26133380 0   asseessments_question asseessments_question_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.asseessments_question
    ADD CONSTRAINT asseessments_question_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.asseessments_question DROP CONSTRAINT asseessments_question_pkey;
       public            u2m65eq7rc7j8s    false    246            �           2606    26133386 ,   asseessments_result asseessments_result_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.asseessments_result
    ADD CONSTRAINT asseessments_result_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.asseessments_result DROP CONSTRAINT asseessments_result_pkey;
       public            u2m65eq7rc7j8s    false    248            �           2606    26133392 .   asseessments_session asseessments_session_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.asseessments_session
    ADD CONSTRAINT asseessments_session_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.asseessments_session DROP CONSTRAINT asseessments_session_pkey;
       public            u2m65eq7rc7j8s    false    250            �           2606    26133243    auth_group auth_group_name_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);
 H   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
       public            u2m65eq7rc7j8s    false    226            �           2606    26133229 R   auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);
 |   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
       public            u2m65eq7rc7j8s    false    228    228            �           2606    26133218 2   auth_group_permissions auth_group_permissions_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
       public            u2m65eq7rc7j8s    false    228            �           2606    26133210    auth_group auth_group_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
       public            u2m65eq7rc7j8s    false    226            �           2606    26133220 F   auth_permission auth_permission_content_type_id_codename_01ab375a_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);
 p   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq;
       public            u2m65eq7rc7j8s    false    224    224            �           2606    26133204 $   auth_permission auth_permission_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
       public            u2m65eq7rc7j8s    false    224            �           2606    28295571 2   cities_light_city cities_light_city_geoname_id_key 
   CONSTRAINT     s   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_geoname_id_key UNIQUE (geoname_id);
 \   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_geoname_id_key;
       public            u2m65eq7rc7j8s    false    347            �           2606    28295569 (   cities_light_city cities_light_city_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_pkey;
       public            u2m65eq7rc7j8s    false    347            �           2606    28295637 M   cities_light_city cities_light_city_region_id_subregion_id_name_cdfc77ea_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_region_id_subregion_id_name_cdfc77ea_uniq UNIQUE (region_id, subregion_id, name);
 w   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_region_id_subregion_id_name_cdfc77ea_uniq;
       public            u2m65eq7rc7j8s    false    347    347    347            �           2606    28295639 M   cities_light_city cities_light_city_region_id_subregion_id_slug_efb2e768_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_region_id_subregion_id_slug_efb2e768_uniq UNIQUE (region_id, subregion_id, slug);
 w   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_region_id_subregion_id_slug_efb2e768_uniq;
       public            u2m65eq7rc7j8s    false    347    347    347            �           2606    28295518 3   cities_light_country cities_light_country_code2_key 
   CONSTRAINT     o   ALTER TABLE ONLY public.cities_light_country
    ADD CONSTRAINT cities_light_country_code2_key UNIQUE (code2);
 ]   ALTER TABLE ONLY public.cities_light_country DROP CONSTRAINT cities_light_country_code2_key;
       public            u2m65eq7rc7j8s    false    343            �           2606    28295520 3   cities_light_country cities_light_country_code3_key 
   CONSTRAINT     o   ALTER TABLE ONLY public.cities_light_country
    ADD CONSTRAINT cities_light_country_code3_key UNIQUE (code3);
 ]   ALTER TABLE ONLY public.cities_light_country DROP CONSTRAINT cities_light_country_code3_key;
       public            u2m65eq7rc7j8s    false    343            �           2606    28295514 8   cities_light_country cities_light_country_geoname_id_key 
   CONSTRAINT     y   ALTER TABLE ONLY public.cities_light_country
    ADD CONSTRAINT cities_light_country_geoname_id_key UNIQUE (geoname_id);
 b   ALTER TABLE ONLY public.cities_light_country DROP CONSTRAINT cities_light_country_geoname_id_key;
       public            u2m65eq7rc7j8s    false    343            �           2606    28295512 .   cities_light_country cities_light_country_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.cities_light_country
    ADD CONSTRAINT cities_light_country_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.cities_light_country DROP CONSTRAINT cities_light_country_pkey;
       public            u2m65eq7rc7j8s    false    343            �           2606    28295543 E   cities_light_region cities_light_region_country_id_name_6e5b3799_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_region
    ADD CONSTRAINT cities_light_region_country_id_name_6e5b3799_uniq UNIQUE (country_id, name);
 o   ALTER TABLE ONLY public.cities_light_region DROP CONSTRAINT cities_light_region_country_id_name_6e5b3799_uniq;
       public            u2m65eq7rc7j8s    false    345    345            �           2606    28295545 E   cities_light_region cities_light_region_country_id_slug_3dd02103_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_region
    ADD CONSTRAINT cities_light_region_country_id_slug_3dd02103_uniq UNIQUE (country_id, slug);
 o   ALTER TABLE ONLY public.cities_light_region DROP CONSTRAINT cities_light_region_country_id_slug_3dd02103_uniq;
       public            u2m65eq7rc7j8s    false    345    345            �           2606    28295530 6   cities_light_region cities_light_region_geoname_id_key 
   CONSTRAINT     w   ALTER TABLE ONLY public.cities_light_region
    ADD CONSTRAINT cities_light_region_geoname_id_key UNIQUE (geoname_id);
 `   ALTER TABLE ONLY public.cities_light_region DROP CONSTRAINT cities_light_region_geoname_id_key;
       public            u2m65eq7rc7j8s    false    345            �           2606    28295528 ,   cities_light_region cities_light_region_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.cities_light_region
    ADD CONSTRAINT cities_light_region_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.cities_light_region DROP CONSTRAINT cities_light_region_pkey;
       public            u2m65eq7rc7j8s    false    345            �           2606    28295609 <   cities_light_subregion cities_light_subregion_geoname_id_key 
   CONSTRAINT     }   ALTER TABLE ONLY public.cities_light_subregion
    ADD CONSTRAINT cities_light_subregion_geoname_id_key UNIQUE (geoname_id);
 f   ALTER TABLE ONLY public.cities_light_subregion DROP CONSTRAINT cities_light_subregion_geoname_id_key;
       public            u2m65eq7rc7j8s    false    349            �           2606    28295607 2   cities_light_subregion cities_light_subregion_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.cities_light_subregion
    ADD CONSTRAINT cities_light_subregion_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.cities_light_subregion DROP CONSTRAINT cities_light_subregion_pkey;
       public            u2m65eq7rc7j8s    false    349            �           2606    26133451 $   company_company company_company_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.company_company
    ADD CONSTRAINT company_company_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.company_company DROP CONSTRAINT company_company_pkey;
       public            u2m65eq7rc7j8s    false    252            �           2606    26133443 +   company_company company_company_user_id_key 
   CONSTRAINT     i   ALTER TABLE ONLY public.company_company
    ADD CONSTRAINT company_company_user_id_key UNIQUE (user_id);
 U   ALTER TABLE ONLY public.company_company DROP CONSTRAINT company_company_user_id_key;
       public            u2m65eq7rc7j8s    false    252            �           2606    26133344 &   django_admin_log django_admin_log_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
       public            u2m65eq7rc7j8s    false    240            �           2606    26133198 E   django_content_type django_content_type_app_label_model_76bd3d3b_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);
 o   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq;
       public            u2m65eq7rc7j8s    false    222    222            �           2606    26133196 ,   django_content_type django_content_type_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
       public            u2m65eq7rc7j8s    false    222            �           2606    26133190 (   django_migrations django_migrations_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.django_migrations DROP CONSTRAINT django_migrations_pkey;
       public            u2m65eq7rc7j8s    false    220            ^           2606    26134157 "   django_session django_session_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
 L   ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
       public            u2m65eq7rc7j8s    false    311            b           2606    26134167 ,   django_site django_site_domain_a2e37b91_uniq 
   CONSTRAINT     i   ALTER TABLE ONLY public.django_site
    ADD CONSTRAINT django_site_domain_a2e37b91_uniq UNIQUE (domain);
 V   ALTER TABLE ONLY public.django_site DROP CONSTRAINT django_site_domain_a2e37b91_uniq;
       public            u2m65eq7rc7j8s    false    313            d           2606    26134165    django_site django_site_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.django_site DROP CONSTRAINT django_site_pkey;
       public            u2m65eq7rc7j8s    false    313                       2606    26133745 ,   job_applicantanswer job_applicantanswer_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.job_applicantanswer
    ADD CONSTRAINT job_applicantanswer_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.job_applicantanswer DROP CONSTRAINT job_applicantanswer_pkey;
       public            u2m65eq7rc7j8s    false    276                       2606    26133751 $   job_application job_application_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.job_application
    ADD CONSTRAINT job_application_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.job_application DROP CONSTRAINT job_application_pkey;
       public            u2m65eq7rc7j8s    false    278            8           2606    26133908 ,   job_completedskills job_completedskills_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.job_completedskills
    ADD CONSTRAINT job_completedskills_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.job_completedskills DROP CONSTRAINT job_completedskills_pkey;
       public            u2m65eq7rc7j8s    false    292            <           2606    26133910 M   job_completedskills job_completedskills_user_id_job_id_skill_id_36997bde_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.job_completedskills
    ADD CONSTRAINT job_completedskills_user_id_job_id_skill_id_36997bde_uniq UNIQUE (user_id, job_id, skill_id);
 w   ALTER TABLE ONLY public.job_completedskills DROP CONSTRAINT job_completedskills_user_id_job_id_skill_id_36997bde_uniq;
       public            u2m65eq7rc7j8s    false    292    292    292            ,           2606    26133866 O   job_job_extracted_skills job_job_extracted_skills_job_id_skill_id_0103678d_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.job_job_extracted_skills
    ADD CONSTRAINT job_job_extracted_skills_job_id_skill_id_0103678d_uniq UNIQUE (job_id, skill_id);
 y   ALTER TABLE ONLY public.job_job_extracted_skills DROP CONSTRAINT job_job_extracted_skills_job_id_skill_id_0103678d_uniq;
       public            u2m65eq7rc7j8s    false    288    288            .           2606    26133821 6   job_job_extracted_skills job_job_extracted_skills_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.job_job_extracted_skills
    ADD CONSTRAINT job_job_extracted_skills_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.job_job_extracted_skills DROP CONSTRAINT job_job_extracted_skills_pkey;
       public            u2m65eq7rc7j8s    false    288                       2606    26133760    job_job job_job_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.job_job
    ADD CONSTRAINT job_job_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.job_job DROP CONSTRAINT job_job_pkey;
       public            u2m65eq7rc7j8s    false    280            2           2606    26133880 G   job_job_requirements job_job_requirements_job_id_skill_id_194ff824_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.job_job_requirements
    ADD CONSTRAINT job_job_requirements_job_id_skill_id_194ff824_uniq UNIQUE (job_id, skill_id);
 q   ALTER TABLE ONLY public.job_job_requirements DROP CONSTRAINT job_job_requirements_job_id_skill_id_194ff824_uniq;
       public            u2m65eq7rc7j8s    false    290    290            4           2606    26133827 .   job_job_requirements job_job_requirements_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.job_job_requirements
    ADD CONSTRAINT job_job_requirements_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.job_job_requirements DROP CONSTRAINT job_job_requirements_pkey;
       public            u2m65eq7rc7j8s    false    290                       2606    26133768    job_mcq job_mcq_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.job_mcq
    ADD CONSTRAINT job_mcq_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.job_mcq DROP CONSTRAINT job_mcq_pkey;
       public            u2m65eq7rc7j8s    false    282            "           2606    26133774    job_savedjob job_savedjob_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.job_savedjob
    ADD CONSTRAINT job_savedjob_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.job_savedjob DROP CONSTRAINT job_savedjob_pkey;
       public            u2m65eq7rc7j8s    false    284            %           2606    26133860 6   job_savedjob job_savedjob_user_id_job_id_64ced2a2_uniq 
   CONSTRAINT     |   ALTER TABLE ONLY public.job_savedjob
    ADD CONSTRAINT job_savedjob_user_id_job_id_64ced2a2_uniq UNIQUE (user_id, job_id);
 `   ALTER TABLE ONLY public.job_savedjob DROP CONSTRAINT job_savedjob_user_id_job_id_64ced2a2_uniq;
       public            u2m65eq7rc7j8s    false    284    284            (           2606    26133782 (   job_skillquestion job_skillquestion_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.job_skillquestion
    ADD CONSTRAINT job_skillquestion_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.job_skillquestion DROP CONSTRAINT job_skillquestion_pkey;
       public            u2m65eq7rc7j8s    false    286            C           2606    26133974 0   messaging_chatmessage messaging_chatmessage_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.messaging_chatmessage
    ADD CONSTRAINT messaging_chatmessage_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.messaging_chatmessage DROP CONSTRAINT messaging_chatmessage_pkey;
       public            u2m65eq7rc7j8s    false    296            @           2606    26133966 2   messaging_conversation messaging_conversation_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.messaging_conversation
    ADD CONSTRAINT messaging_conversation_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.messaging_conversation DROP CONSTRAINT messaging_conversation_pkey;
       public            u2m65eq7rc7j8s    false    294            F           2606    26134007 :   notifications_notification notifications_notification_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.notifications_notification
    ADD CONSTRAINT notifications_notification_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.notifications_notification DROP CONSTRAINT notifications_notification_pkey;
       public            u2m65eq7rc7j8s    false    298            I           2606    26134019 H   onboarding_generalknowledgeanswer onboarding_generalknowledgeanswer_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.onboarding_generalknowledgeanswer
    ADD CONSTRAINT onboarding_generalknowledgeanswer_pkey PRIMARY KEY (id);
 r   ALTER TABLE ONLY public.onboarding_generalknowledgeanswer DROP CONSTRAINT onboarding_generalknowledgeanswer_pkey;
       public            u2m65eq7rc7j8s    false    300            L           2606    26134025 L   onboarding_generalknowledgequestion onboarding_generalknowledgequestion_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.onboarding_generalknowledgequestion
    ADD CONSTRAINT onboarding_generalknowledgequestion_pkey PRIMARY KEY (id);
 v   ALTER TABLE ONLY public.onboarding_generalknowledgequestion DROP CONSTRAINT onboarding_generalknowledgequestion_pkey;
       public            u2m65eq7rc7j8s    false    302            P           2606    26134031 4   onboarding_quizresponse onboarding_quizresponse_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.onboarding_quizresponse
    ADD CONSTRAINT onboarding_quizresponse_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.onboarding_quizresponse DROP CONSTRAINT onboarding_quizresponse_pkey;
       public            u2m65eq7rc7j8s    false    304                       2606    26133699 *   resume_contactinfo resume_contactinfo_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.resume_contactinfo
    ADD CONSTRAINT resume_contactinfo_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.resume_contactinfo DROP CONSTRAINT resume_contactinfo_pkey;
       public            u2m65eq7rc7j8s    false    274            �           2606    26133469 &   resume_education resume_education_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.resume_education
    ADD CONSTRAINT resume_education_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.resume_education DROP CONSTRAINT resume_education_pkey;
       public            u2m65eq7rc7j8s    false    254            �           2606    26133475 (   resume_experience resume_experience_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.resume_experience
    ADD CONSTRAINT resume_experience_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.resume_experience DROP CONSTRAINT resume_experience_pkey;
       public            u2m65eq7rc7j8s    false    256            W           2606    26134089 $   resume_language resume_language_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.resume_language
    ADD CONSTRAINT resume_language_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.resume_language DROP CONSTRAINT resume_language_pkey;
       public            u2m65eq7rc7j8s    false    308            �           2606    26133612     resume_resume resume_resume_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.resume_resume
    ADD CONSTRAINT resume_resume_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.resume_resume DROP CONSTRAINT resume_resume_pkey;
       public            u2m65eq7rc7j8s    false    258                       2606    26133562 .   resume_resume_skills resume_resume_skills_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.resume_resume_skills
    ADD CONSTRAINT resume_resume_skills_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.resume_resume_skills DROP CONSTRAINT resume_resume_skills_pkey;
       public            u2m65eq7rc7j8s    false    270                       2606    26133623 J   resume_resume_skills resume_resume_skills_resume_id_skill_id_b6933a1d_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.resume_resume_skills
    ADD CONSTRAINT resume_resume_skills_resume_id_skill_id_b6933a1d_uniq UNIQUE (resume_id, skill_id);
 t   ALTER TABLE ONLY public.resume_resume_skills DROP CONSTRAINT resume_resume_skills_resume_id_skill_id_b6933a1d_uniq;
       public            u2m65eq7rc7j8s    false    270    270            �           2606    26134140 1   resume_resume resume_resume_user_id_0b155703_uniq 
   CONSTRAINT     o   ALTER TABLE ONLY public.resume_resume
    ADD CONSTRAINT resume_resume_user_id_0b155703_uniq UNIQUE (user_id);
 [   ALTER TABLE ONLY public.resume_resume DROP CONSTRAINT resume_resume_user_id_0b155703_uniq;
       public            u2m65eq7rc7j8s    false    258            �           2606    26133673 ^   resume_resumedoc_extracted_skills resume_resumedoc_extract_resumedoc_id_skill_id_c69684e0_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills
    ADD CONSTRAINT resume_resumedoc_extract_resumedoc_id_skill_id_c69684e0_uniq UNIQUE (resumedoc_id, skill_id);
 �   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills DROP CONSTRAINT resume_resumedoc_extract_resumedoc_id_skill_id_c69684e0_uniq;
       public            u2m65eq7rc7j8s    false    268    268            �           2606    26133515 H   resume_resumedoc_extracted_skills resume_resumedoc_extracted_skills_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills
    ADD CONSTRAINT resume_resumedoc_extracted_skills_pkey PRIMARY KEY (id);
 r   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills DROP CONSTRAINT resume_resumedoc_extracted_skills_pkey;
       public            u2m65eq7rc7j8s    false    268            �           2606    26133663 &   resume_resumedoc resume_resumedoc_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.resume_resumedoc
    ADD CONSTRAINT resume_resumedoc_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.resume_resumedoc DROP CONSTRAINT resume_resumedoc_pkey;
       public            u2m65eq7rc7j8s    false    266            �           2606    26133545 -   resume_resumedoc resume_resumedoc_user_id_key 
   CONSTRAINT     k   ALTER TABLE ONLY public.resume_resumedoc
    ADD CONSTRAINT resume_resumedoc_user_id_key UNIQUE (user_id);
 W   ALTER TABLE ONLY public.resume_resumedoc DROP CONSTRAINT resume_resumedoc_user_id_key;
       public            u2m65eq7rc7j8s    false    266            �           2606    26133501 4   resume_skill_categories resume_skill_categories_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.resume_skill_categories
    ADD CONSTRAINT resume_skill_categories_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.resume_skill_categories DROP CONSTRAINT resume_skill_categories_pkey;
       public            u2m65eq7rc7j8s    false    264            �           2606    26133517 W   resume_skill_categories resume_skill_categories_skill_id_skillcategory_id_ee7ac343_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.resume_skill_categories
    ADD CONSTRAINT resume_skill_categories_skill_id_skillcategory_id_ee7ac343_uniq UNIQUE (skill_id, skillcategory_id);
 �   ALTER TABLE ONLY public.resume_skill_categories DROP CONSTRAINT resume_skill_categories_skill_id_skillcategory_id_ee7ac343_uniq;
       public            u2m65eq7rc7j8s    false    264    264            �           2606    26133495    resume_skill resume_skill_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.resume_skill
    ADD CONSTRAINT resume_skill_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.resume_skill DROP CONSTRAINT resume_skill_pkey;
       public            u2m65eq7rc7j8s    false    262            �           2606    26133489 .   resume_skillcategory resume_skillcategory_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.resume_skillcategory
    ADD CONSTRAINT resume_skillcategory_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.resume_skillcategory DROP CONSTRAINT resume_skillcategory_pkey;
       public            u2m65eq7rc7j8s    false    260            Z           2606    26134120 ,   resume_userlanguage resume_userlanguage_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.resume_userlanguage
    ADD CONSTRAINT resume_userlanguage_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.resume_userlanguage DROP CONSTRAINT resume_userlanguage_pkey;
       public            u2m65eq7rc7j8s    false    310            S           2606    26134076 *   resume_userprofile resume_userprofile_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.resume_userprofile
    ADD CONSTRAINT resume_userprofile_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.resume_userprofile DROP CONSTRAINT resume_userprofile_pkey;
       public            u2m65eq7rc7j8s    false    306            U           2606    26134078 1   resume_userprofile resume_userprofile_user_id_key 
   CONSTRAINT     o   ALTER TABLE ONLY public.resume_userprofile
    ADD CONSTRAINT resume_userprofile_user_id_key UNIQUE (user_id);
 [   ALTER TABLE ONLY public.resume_userprofile DROP CONSTRAINT resume_userprofile_user_id_key;
       public            u2m65eq7rc7j8s    false    306                       2606    26133693 0   resume_workexperience resume_workexperience_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.resume_workexperience
    ADD CONSTRAINT resume_workexperience_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.resume_workexperience DROP CONSTRAINT resume_workexperience_pkey;
       public            u2m65eq7rc7j8s    false    272            f           2606    26134237 4   social_auth_association social_auth_association_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.social_auth_association
    ADD CONSTRAINT social_auth_association_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.social_auth_association DROP CONSTRAINT social_auth_association_pkey;
       public            u2m65eq7rc7j8s    false    315            h           2606    26134215 O   social_auth_association social_auth_association_server_url_handle_078befa2_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.social_auth_association
    ADD CONSTRAINT social_auth_association_server_url_handle_078befa2_uniq UNIQUE (server_url, handle);
 y   ALTER TABLE ONLY public.social_auth_association DROP CONSTRAINT social_auth_association_server_url_handle_078befa2_uniq;
       public            u2m65eq7rc7j8s    false    315    315            l           2606    26134213 :   social_auth_code social_auth_code_email_code_801b2d02_uniq 
   CONSTRAINT     |   ALTER TABLE ONLY public.social_auth_code
    ADD CONSTRAINT social_auth_code_email_code_801b2d02_uniq UNIQUE (email, code);
 d   ALTER TABLE ONLY public.social_auth_code DROP CONSTRAINT social_auth_code_email_code_801b2d02_uniq;
       public            u2m65eq7rc7j8s    false    317    317            n           2606    26134248 &   social_auth_code social_auth_code_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.social_auth_code
    ADD CONSTRAINT social_auth_code_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.social_auth_code DROP CONSTRAINT social_auth_code_pkey;
       public            u2m65eq7rc7j8s    false    317            q           2606    26134260 (   social_auth_nonce social_auth_nonce_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.social_auth_nonce
    ADD CONSTRAINT social_auth_nonce_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.social_auth_nonce DROP CONSTRAINT social_auth_nonce_pkey;
       public            u2m65eq7rc7j8s    false    319            s           2606    26134202 K   social_auth_nonce social_auth_nonce_server_url_timestamp_salt_f6284463_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.social_auth_nonce
    ADD CONSTRAINT social_auth_nonce_server_url_timestamp_salt_f6284463_uniq UNIQUE (server_url, "timestamp", salt);
 u   ALTER TABLE ONLY public.social_auth_nonce DROP CONSTRAINT social_auth_nonce_server_url_timestamp_salt_f6284463_uniq;
       public            u2m65eq7rc7j8s    false    319    319    319            |           2606    26134269 ,   social_auth_partial social_auth_partial_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.social_auth_partial
    ADD CONSTRAINT social_auth_partial_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.social_auth_partial DROP CONSTRAINT social_auth_partial_pkey;
       public            u2m65eq7rc7j8s    false    323            u           2606    26134282 :   social_auth_usersocialauth social_auth_usersocialauth_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.social_auth_usersocialauth
    ADD CONSTRAINT social_auth_usersocialauth_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.social_auth_usersocialauth DROP CONSTRAINT social_auth_usersocialauth_pkey;
       public            u2m65eq7rc7j8s    false    321            w           2606    26134198 P   social_auth_usersocialauth social_auth_usersocialauth_provider_uid_e6b5e668_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.social_auth_usersocialauth
    ADD CONSTRAINT social_auth_usersocialauth_provider_uid_e6b5e668_uniq UNIQUE (provider, uid);
 z   ALTER TABLE ONLY public.social_auth_usersocialauth DROP CONSTRAINT social_auth_usersocialauth_provider_uid_e6b5e668_uniq;
       public            u2m65eq7rc7j8s    false    321    321            �           2606    26134363 4   social_features_comment social_features_comment_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.social_features_comment
    ADD CONSTRAINT social_features_comment_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.social_features_comment DROP CONSTRAINT social_features_comment_pkey;
       public            u2m65eq7rc7j8s    false    333            �           2606    26134355 2   social_features_follow social_features_follow_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.social_features_follow
    ADD CONSTRAINT social_features_follow_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.social_features_follow DROP CONSTRAINT social_features_follow_pkey;
       public            u2m65eq7rc7j8s    false    331            �           2606    26134349 .   social_features_like social_features_like_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.social_features_like
    ADD CONSTRAINT social_features_like_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.social_features_like DROP CONSTRAINT social_features_like_pkey;
       public            u2m65eq7rc7j8s    false    329            �           2606    26134309 4   social_features_message social_features_message_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.social_features_message
    ADD CONSTRAINT social_features_message_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.social_features_message DROP CONSTRAINT social_features_message_pkey;
       public            u2m65eq7rc7j8s    false    325            �           2606    26134302 .   social_features_post social_features_post_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.social_features_post
    ADD CONSTRAINT social_features_post_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.social_features_post DROP CONSTRAINT social_features_post_pkey;
       public            u2m65eq7rc7j8s    false    324            �           2606    26134341 <   social_features_userprofile social_features_userprofile_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY public.social_features_userprofile
    ADD CONSTRAINT social_features_userprofile_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.social_features_userprofile DROP CONSTRAINT social_features_userprofile_pkey;
       public            u2m65eq7rc7j8s    false    327            �           2606    26134343 C   social_features_userprofile social_features_userprofile_user_id_key 
   CONSTRAINT     �   ALTER TABLE ONLY public.social_features_userprofile
    ADD CONSTRAINT social_features_userprofile_user_id_key UNIQUE (user_id);
 m   ALTER TABLE ONLY public.social_features_userprofile DROP CONSTRAINT social_features_userprofile_user_id_key;
       public            u2m65eq7rc7j8s    false    327            �           2606    26134413 <   socialaccount_socialaccount socialaccount_socialaccount_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY public.socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.socialaccount_socialaccount DROP CONSTRAINT socialaccount_socialaccount_pkey;
       public            u2m65eq7rc7j8s    false    335            �           2606    26134475 R   socialaccount_socialaccount socialaccount_socialaccount_provider_uid_fc810c6e_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_provider_uid_fc810c6e_uniq UNIQUE (provider, uid);
 |   ALTER TABLE ONLY public.socialaccount_socialaccount DROP CONSTRAINT socialaccount_socialaccount_provider_uid_fc810c6e_uniq;
       public            u2m65eq7rc7j8s    false    335    335            �           2606    26134445 Y   socialaccount_socialapp_sites socialaccount_socialapp__socialapp_id_site_id_71a9a768_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp__socialapp_id_site_id_71a9a768_uniq UNIQUE (socialapp_id, site_id);
 �   ALTER TABLE ONLY public.socialaccount_socialapp_sites DROP CONSTRAINT socialaccount_socialapp__socialapp_id_site_id_71a9a768_uniq;
       public            u2m65eq7rc7j8s    false    339    339            �           2606    26134419 4   socialaccount_socialapp socialaccount_socialapp_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.socialaccount_socialapp
    ADD CONSTRAINT socialaccount_socialapp_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.socialaccount_socialapp DROP CONSTRAINT socialaccount_socialapp_pkey;
       public            u2m65eq7rc7j8s    false    337            �           2606    26134425 @   socialaccount_socialapp_sites socialaccount_socialapp_sites_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY public.socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_sites_pkey PRIMARY KEY (id);
 j   ALTER TABLE ONLY public.socialaccount_socialapp_sites DROP CONSTRAINT socialaccount_socialapp_sites_pkey;
       public            u2m65eq7rc7j8s    false    339            �           2606    26134435 S   socialaccount_socialtoken socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq UNIQUE (app_id, account_id);
 }   ALTER TABLE ONLY public.socialaccount_socialtoken DROP CONSTRAINT socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq;
       public            u2m65eq7rc7j8s    false    341    341            �           2606    26134433 8   socialaccount_socialtoken socialaccount_socialtoken_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_socialtoken_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.socialaccount_socialtoken DROP CONSTRAINT socialaccount_socialtoken_pkey;
       public            u2m65eq7rc7j8s    false    341            �           2606    26133256    users_user users_user_email_key 
   CONSTRAINT     [   ALTER TABLE ONLY public.users_user
    ADD CONSTRAINT users_user_email_key UNIQUE (email);
 I   ALTER TABLE ONLY public.users_user DROP CONSTRAINT users_user_email_key;
       public            u2m65eq7rc7j8s    false    230            �           2606    26133262 (   users_user_groups users_user_groups_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.users_user_groups
    ADD CONSTRAINT users_user_groups_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.users_user_groups DROP CONSTRAINT users_user_groups_pkey;
       public            u2m65eq7rc7j8s    false    232            �           2606    26133272 B   users_user_groups users_user_groups_user_id_group_id_b88eab82_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.users_user_groups
    ADD CONSTRAINT users_user_groups_user_id_group_id_b88eab82_uniq UNIQUE (user_id, group_id);
 l   ALTER TABLE ONLY public.users_user_groups DROP CONSTRAINT users_user_groups_user_id_group_id_b88eab82_uniq;
       public            u2m65eq7rc7j8s    false    232    232            �           2606    26133252    users_user users_user_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.users_user
    ADD CONSTRAINT users_user_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.users_user DROP CONSTRAINT users_user_pkey;
       public            u2m65eq7rc7j8s    false    230            �           2606    26133268 <   users_user_user_permissions users_user_user_permissions_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY public.users_user_user_permissions
    ADD CONSTRAINT users_user_user_permissions_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.users_user_user_permissions DROP CONSTRAINT users_user_user_permissions_pkey;
       public            u2m65eq7rc7j8s    false    234            �           2606    26133286 [   users_user_user_permissions users_user_user_permissions_user_id_permission_id_43338c45_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.users_user_user_permissions
    ADD CONSTRAINT users_user_user_permissions_user_id_permission_id_43338c45_uniq UNIQUE (user_id, permission_id);
 �   ALTER TABLE ONLY public.users_user_user_permissions DROP CONSTRAINT users_user_user_permissions_user_id_permission_id_43338c45_uniq;
       public            u2m65eq7rc7j8s    false    234    234            �           2606    26133254 "   users_user users_user_username_key 
   CONSTRAINT     a   ALTER TABLE ONLY public.users_user
    ADD CONSTRAINT users_user_username_key UNIQUE (username);
 L   ALTER TABLE ONLY public.users_user DROP CONSTRAINT users_user_username_key;
       public            u2m65eq7rc7j8s    false    230            �           1259    26133335    account_emailaddress_upper    INDEX     k   CREATE INDEX account_emailaddress_upper ON public.account_emailaddress USING btree (upper((email)::text));
 .   DROP INDEX public.account_emailaddress_upper;
       public            u2m65eq7rc7j8s    false    236    236            �           1259    26133321 %   account_emailaddress_user_id_2c513194    INDEX     i   CREATE INDEX account_emailaddress_user_id_2c513194 ON public.account_emailaddress USING btree (user_id);
 9   DROP INDEX public.account_emailaddress_user_id_2c513194;
       public            u2m65eq7rc7j8s    false    236            �           1259    26133328 3   account_emailconfirmation_email_address_id_5b7f8c58    INDEX     �   CREATE INDEX account_emailconfirmation_email_address_id_5b7f8c58 ON public.account_emailconfirmation USING btree (email_address_id);
 G   DROP INDEX public.account_emailconfirmation_email_address_id_5b7f8c58;
       public            u2m65eq7rc7j8s    false    238            �           1259    26133327 +   account_emailconfirmation_key_f43612bd_like    INDEX     �   CREATE INDEX account_emailconfirmation_key_f43612bd_like ON public.account_emailconfirmation USING btree (key varchar_pattern_ops);
 ?   DROP INDEX public.account_emailconfirmation_key_f43612bd_like;
       public            u2m65eq7rc7j8s    false    238            �           1259    26133434 (   asseessments_option_question_id_cc527d25    INDEX     o   CREATE INDEX asseessments_option_question_id_cc527d25 ON public.asseessments_option USING btree (question_id);
 <   DROP INDEX public.asseessments_option_question_id_cc527d25;
       public            u2m65eq7rc7j8s    false    244            �           1259    26133433 ,   asseessments_question_assessment_id_421d6d70    INDEX     w   CREATE INDEX asseessments_question_assessment_id_421d6d70 ON public.asseessments_question USING btree (assessment_id);
 @   DROP INDEX public.asseessments_question_assessment_id_421d6d70;
       public            u2m65eq7rc7j8s    false    246            �           1259    26133430 (   asseessments_result_question_id_4f643745    INDEX     o   CREATE INDEX asseessments_result_question_id_4f643745 ON public.asseessments_result USING btree (question_id);
 <   DROP INDEX public.asseessments_result_question_id_4f643745;
       public            u2m65eq7rc7j8s    false    248            �           1259    26133431 /   asseessments_result_selected_option_id_5bc3c3c3    INDEX     }   CREATE INDEX asseessments_result_selected_option_id_5bc3c3c3 ON public.asseessments_result USING btree (selected_option_id);
 C   DROP INDEX public.asseessments_result_selected_option_id_5bc3c3c3;
       public            u2m65eq7rc7j8s    false    248            �           1259    26133432 '   asseessments_result_session_id_3c5fd623    INDEX     m   CREATE INDEX asseessments_result_session_id_3c5fd623 ON public.asseessments_result USING btree (session_id);
 ;   DROP INDEX public.asseessments_result_session_id_3c5fd623;
       public            u2m65eq7rc7j8s    false    248            �           1259    26133398 +   asseessments_session_assessment_id_22cebda1    INDEX     u   CREATE INDEX asseessments_session_assessment_id_22cebda1 ON public.asseessments_session USING btree (assessment_id);
 ?   DROP INDEX public.asseessments_session_assessment_id_22cebda1;
       public            u2m65eq7rc7j8s    false    250            �           1259    26133429 %   asseessments_session_user_id_3909b917    INDEX     i   CREATE INDEX asseessments_session_user_id_3909b917 ON public.asseessments_session USING btree (user_id);
 9   DROP INDEX public.asseessments_session_user_id_3909b917;
       public            u2m65eq7rc7j8s    false    250            �           1259    26133244    auth_group_name_a6ea08ec_like    INDEX     h   CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);
 1   DROP INDEX public.auth_group_name_a6ea08ec_like;
       public            u2m65eq7rc7j8s    false    226            �           1259    26133240 (   auth_group_permissions_group_id_b120cbf9    INDEX     o   CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);
 <   DROP INDEX public.auth_group_permissions_group_id_b120cbf9;
       public            u2m65eq7rc7j8s    false    228            �           1259    26133241 -   auth_group_permissions_permission_id_84c5c92e    INDEX     y   CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);
 A   DROP INDEX public.auth_group_permissions_permission_id_84c5c92e;
       public            u2m65eq7rc7j8s    false    228            �           1259    26133226 (   auth_permission_content_type_id_2f476e4b    INDEX     o   CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);
 <   DROP INDEX public.auth_permission_content_type_id_2f476e4b;
       public            u2m65eq7rc7j8s    false    224            �           1259    28295593 %   cities_light_city_country_id_cf310fd2    INDEX     i   CREATE INDEX cities_light_city_country_id_cf310fd2 ON public.cities_light_city USING btree (country_id);
 9   DROP INDEX public.cities_light_city_country_id_cf310fd2;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295595 '   cities_light_city_feature_code_d43c9217    INDEX     m   CREATE INDEX cities_light_city_feature_code_d43c9217 ON public.cities_light_city USING btree (feature_code);
 ;   DROP INDEX public.cities_light_city_feature_code_d43c9217;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295596 ,   cities_light_city_feature_code_d43c9217_like    INDEX     �   CREATE INDEX cities_light_city_feature_code_d43c9217_like ON public.cities_light_city USING btree (feature_code varchar_pattern_ops);
 @   DROP INDEX public.cities_light_city_feature_code_d43c9217_like;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295590    cities_light_city_name_4859e2a5    INDEX     ]   CREATE INDEX cities_light_city_name_4859e2a5 ON public.cities_light_city USING btree (name);
 3   DROP INDEX public.cities_light_city_name_4859e2a5;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295591 $   cities_light_city_name_4859e2a5_like    INDEX     v   CREATE INDEX cities_light_city_name_4859e2a5_like ON public.cities_light_city USING btree (name varchar_pattern_ops);
 8   DROP INDEX public.cities_light_city_name_4859e2a5_like;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295586 %   cities_light_city_name_ascii_1e56323b    INDEX     i   CREATE INDEX cities_light_city_name_ascii_1e56323b ON public.cities_light_city USING btree (name_ascii);
 9   DROP INDEX public.cities_light_city_name_ascii_1e56323b;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295587 *   cities_light_city_name_ascii_1e56323b_like    INDEX     �   CREATE INDEX cities_light_city_name_ascii_1e56323b_like ON public.cities_light_city USING btree (name_ascii varchar_pattern_ops);
 >   DROP INDEX public.cities_light_city_name_ascii_1e56323b_like;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295594 %   cities_light_city_population_d597eeb6    INDEX     i   CREATE INDEX cities_light_city_population_d597eeb6 ON public.cities_light_city USING btree (population);
 9   DROP INDEX public.cities_light_city_population_d597eeb6;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295592 $   cities_light_city_region_id_f7ab977b    INDEX     g   CREATE INDEX cities_light_city_region_id_f7ab977b ON public.cities_light_city USING btree (region_id);
 8   DROP INDEX public.cities_light_city_region_id_f7ab977b;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295588    cities_light_city_slug_cb2251f8    INDEX     ]   CREATE INDEX cities_light_city_slug_cb2251f8 ON public.cities_light_city USING btree (slug);
 3   DROP INDEX public.cities_light_city_slug_cb2251f8;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295589 $   cities_light_city_slug_cb2251f8_like    INDEX     v   CREATE INDEX cities_light_city_slug_cb2251f8_like ON public.cities_light_city USING btree (slug varchar_pattern_ops);
 8   DROP INDEX public.cities_light_city_slug_cb2251f8_like;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295635 '   cities_light_city_subregion_id_0926d2ad    INDEX     m   CREATE INDEX cities_light_city_subregion_id_0926d2ad ON public.cities_light_city USING btree (subregion_id);
 ;   DROP INDEX public.cities_light_city_subregion_id_0926d2ad;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295598 #   cities_light_city_timezone_0fb51b1e    INDEX     e   CREATE INDEX cities_light_city_timezone_0fb51b1e ON public.cities_light_city USING btree (timezone);
 7   DROP INDEX public.cities_light_city_timezone_0fb51b1e;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295599 (   cities_light_city_timezone_0fb51b1e_like    INDEX     ~   CREATE INDEX cities_light_city_timezone_0fb51b1e_like ON public.cities_light_city USING btree (timezone varchar_pattern_ops);
 <   DROP INDEX public.cities_light_city_timezone_0fb51b1e_like;
       public            u2m65eq7rc7j8s    false    347            �           1259    28295536 (   cities_light_country_code2_69c32e9a_like    INDEX     ~   CREATE INDEX cities_light_country_code2_69c32e9a_like ON public.cities_light_country USING btree (code2 varchar_pattern_ops);
 <   DROP INDEX public.cities_light_country_code2_69c32e9a_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295537 (   cities_light_country_code3_89d251fa_like    INDEX     ~   CREATE INDEX cities_light_country_code3_89d251fa_like ON public.cities_light_country USING btree (code3 varchar_pattern_ops);
 <   DROP INDEX public.cities_light_country_code3_89d251fa_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295538 '   cities_light_country_continent_e2c412a4    INDEX     m   CREATE INDEX cities_light_country_continent_e2c412a4 ON public.cities_light_country USING btree (continent);
 ;   DROP INDEX public.cities_light_country_continent_e2c412a4;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295539 ,   cities_light_country_continent_e2c412a4_like    INDEX     �   CREATE INDEX cities_light_country_continent_e2c412a4_like ON public.cities_light_country USING btree (continent varchar_pattern_ops);
 @   DROP INDEX public.cities_light_country_continent_e2c412a4_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295597 "   cities_light_country_name_1d61d0d2    INDEX     c   CREATE INDEX cities_light_country_name_1d61d0d2 ON public.cities_light_country USING btree (name);
 6   DROP INDEX public.cities_light_country_name_1d61d0d2;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295535 '   cities_light_country_name_1d61d0d2_like    INDEX     |   CREATE INDEX cities_light_country_name_1d61d0d2_like ON public.cities_light_country USING btree (name varchar_pattern_ops);
 ;   DROP INDEX public.cities_light_country_name_1d61d0d2_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295531 (   cities_light_country_name_ascii_648cc5e3    INDEX     o   CREATE INDEX cities_light_country_name_ascii_648cc5e3 ON public.cities_light_country USING btree (name_ascii);
 <   DROP INDEX public.cities_light_country_name_ascii_648cc5e3;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295532 -   cities_light_country_name_ascii_648cc5e3_like    INDEX     �   CREATE INDEX cities_light_country_name_ascii_648cc5e3_like ON public.cities_light_country USING btree (name_ascii varchar_pattern_ops);
 A   DROP INDEX public.cities_light_country_name_ascii_648cc5e3_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295533 "   cities_light_country_slug_3707a22c    INDEX     c   CREATE INDEX cities_light_country_slug_3707a22c ON public.cities_light_country USING btree (slug);
 6   DROP INDEX public.cities_light_country_slug_3707a22c;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295534 '   cities_light_country_slug_3707a22c_like    INDEX     |   CREATE INDEX cities_light_country_slug_3707a22c_like ON public.cities_light_country USING btree (slug varchar_pattern_ops);
 ;   DROP INDEX public.cities_light_country_slug_3707a22c_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295540 !   cities_light_country_tld_1fb2faaa    INDEX     a   CREATE INDEX cities_light_country_tld_1fb2faaa ON public.cities_light_country USING btree (tld);
 5   DROP INDEX public.cities_light_country_tld_1fb2faaa;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295541 &   cities_light_country_tld_1fb2faaa_like    INDEX     z   CREATE INDEX cities_light_country_tld_1fb2faaa_like ON public.cities_light_country USING btree (tld varchar_pattern_ops);
 :   DROP INDEX public.cities_light_country_tld_1fb2faaa_like;
       public            u2m65eq7rc7j8s    false    343            �           1259    28295561 '   cities_light_region_country_id_b2782d49    INDEX     m   CREATE INDEX cities_light_region_country_id_b2782d49 ON public.cities_light_region USING btree (country_id);
 ;   DROP INDEX public.cities_light_region_country_id_b2782d49;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295559 )   cities_light_region_geoname_code_1b0d4e58    INDEX     q   CREATE INDEX cities_light_region_geoname_code_1b0d4e58 ON public.cities_light_region USING btree (geoname_code);
 =   DROP INDEX public.cities_light_region_geoname_code_1b0d4e58;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295560 .   cities_light_region_geoname_code_1b0d4e58_like    INDEX     �   CREATE INDEX cities_light_region_geoname_code_1b0d4e58_like ON public.cities_light_region USING btree (geoname_code varchar_pattern_ops);
 B   DROP INDEX public.cities_light_region_geoname_code_1b0d4e58_like;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295555 !   cities_light_region_name_775f9496    INDEX     a   CREATE INDEX cities_light_region_name_775f9496 ON public.cities_light_region USING btree (name);
 5   DROP INDEX public.cities_light_region_name_775f9496;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295556 &   cities_light_region_name_775f9496_like    INDEX     z   CREATE INDEX cities_light_region_name_775f9496_like ON public.cities_light_region USING btree (name varchar_pattern_ops);
 :   DROP INDEX public.cities_light_region_name_775f9496_like;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295551 '   cities_light_region_name_ascii_f085cb82    INDEX     m   CREATE INDEX cities_light_region_name_ascii_f085cb82 ON public.cities_light_region USING btree (name_ascii);
 ;   DROP INDEX public.cities_light_region_name_ascii_f085cb82;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295552 ,   cities_light_region_name_ascii_f085cb82_like    INDEX     �   CREATE INDEX cities_light_region_name_ascii_f085cb82_like ON public.cities_light_region USING btree (name_ascii varchar_pattern_ops);
 @   DROP INDEX public.cities_light_region_name_ascii_f085cb82_like;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295553 !   cities_light_region_slug_1653969f    INDEX     a   CREATE INDEX cities_light_region_slug_1653969f ON public.cities_light_region USING btree (slug);
 5   DROP INDEX public.cities_light_region_slug_1653969f;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295554 &   cities_light_region_slug_1653969f_like    INDEX     z   CREATE INDEX cities_light_region_slug_1653969f_like ON public.cities_light_region USING btree (slug varchar_pattern_ops);
 :   DROP INDEX public.cities_light_region_slug_1653969f_like;
       public            u2m65eq7rc7j8s    false    345            �           1259    28295633 *   cities_light_subregion_country_id_9b32b484    INDEX     s   CREATE INDEX cities_light_subregion_country_id_9b32b484 ON public.cities_light_subregion USING btree (country_id);
 >   DROP INDEX public.cities_light_subregion_country_id_9b32b484;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295631 ,   cities_light_subregion_geoname_code_843acdc3    INDEX     w   CREATE INDEX cities_light_subregion_geoname_code_843acdc3 ON public.cities_light_subregion USING btree (geoname_code);
 @   DROP INDEX public.cities_light_subregion_geoname_code_843acdc3;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295632 1   cities_light_subregion_geoname_code_843acdc3_like    INDEX     �   CREATE INDEX cities_light_subregion_geoname_code_843acdc3_like ON public.cities_light_subregion USING btree (geoname_code varchar_pattern_ops);
 E   DROP INDEX public.cities_light_subregion_geoname_code_843acdc3_like;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295625 $   cities_light_subregion_name_2882337e    INDEX     g   CREATE INDEX cities_light_subregion_name_2882337e ON public.cities_light_subregion USING btree (name);
 8   DROP INDEX public.cities_light_subregion_name_2882337e;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295626 )   cities_light_subregion_name_2882337e_like    INDEX     �   CREATE INDEX cities_light_subregion_name_2882337e_like ON public.cities_light_subregion USING btree (name varchar_pattern_ops);
 =   DROP INDEX public.cities_light_subregion_name_2882337e_like;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295627 *   cities_light_subregion_name_ascii_ecf9a336    INDEX     s   CREATE INDEX cities_light_subregion_name_ascii_ecf9a336 ON public.cities_light_subregion USING btree (name_ascii);
 >   DROP INDEX public.cities_light_subregion_name_ascii_ecf9a336;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295628 /   cities_light_subregion_name_ascii_ecf9a336_like    INDEX     �   CREATE INDEX cities_light_subregion_name_ascii_ecf9a336_like ON public.cities_light_subregion USING btree (name_ascii varchar_pattern_ops);
 C   DROP INDEX public.cities_light_subregion_name_ascii_ecf9a336_like;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295634 )   cities_light_subregion_region_id_c6e0b71f    INDEX     q   CREATE INDEX cities_light_subregion_region_id_c6e0b71f ON public.cities_light_subregion USING btree (region_id);
 =   DROP INDEX public.cities_light_subregion_region_id_c6e0b71f;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295629 $   cities_light_subregion_slug_43494546    INDEX     g   CREATE INDEX cities_light_subregion_slug_43494546 ON public.cities_light_subregion USING btree (slug);
 8   DROP INDEX public.cities_light_subregion_slug_43494546;
       public            u2m65eq7rc7j8s    false    349            �           1259    28295630 )   cities_light_subregion_slug_43494546_like    INDEX     �   CREATE INDEX cities_light_subregion_slug_43494546_like ON public.cities_light_subregion USING btree (slug varchar_pattern_ops);
 =   DROP INDEX public.cities_light_subregion_slug_43494546_like;
       public            u2m65eq7rc7j8s    false    349            �           1259    26133355 )   django_admin_log_content_type_id_c4bce8eb    INDEX     q   CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);
 =   DROP INDEX public.django_admin_log_content_type_id_c4bce8eb;
       public            u2m65eq7rc7j8s    false    240            �           1259    26133356 !   django_admin_log_user_id_c564eba6    INDEX     a   CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);
 5   DROP INDEX public.django_admin_log_user_id_c564eba6;
       public            u2m65eq7rc7j8s    false    240            \           1259    26134159 #   django_session_expire_date_a5c62663    INDEX     e   CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);
 7   DROP INDEX public.django_session_expire_date_a5c62663;
       public            u2m65eq7rc7j8s    false    311            _           1259    26134158 (   django_session_session_key_c0390e0f_like    INDEX     ~   CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);
 <   DROP INDEX public.django_session_session_key_c0390e0f_like;
       public            u2m65eq7rc7j8s    false    311            `           1259    26134168     django_site_domain_a2e37b91_like    INDEX     n   CREATE INDEX django_site_domain_a2e37b91_like ON public.django_site USING btree (domain varchar_pattern_ops);
 4   DROP INDEX public.django_site_domain_a2e37b91_like;
       public            u2m65eq7rc7j8s    false    313                       1259    26133896 )   job_applicantanswer_applicant_id_237a7f43    INDEX     q   CREATE INDEX job_applicantanswer_applicant_id_237a7f43 ON public.job_applicantanswer USING btree (applicant_id);
 =   DROP INDEX public.job_applicantanswer_applicant_id_237a7f43;
       public            u2m65eq7rc7j8s    false    276                       1259    26133949 +   job_applicantanswer_application_id_b8401d6a    INDEX     u   CREATE INDEX job_applicantanswer_application_id_b8401d6a ON public.job_applicantanswer USING btree (application_id);
 ?   DROP INDEX public.job_applicantanswer_application_id_b8401d6a;
       public            u2m65eq7rc7j8s    false    276                       1259    26133897 #   job_applicantanswer_job_id_ed8cef68    INDEX     e   CREATE INDEX job_applicantanswer_job_id_ed8cef68 ON public.job_applicantanswer USING btree (job_id);
 7   DROP INDEX public.job_applicantanswer_job_id_ed8cef68;
       public            u2m65eq7rc7j8s    false    276                       1259    26133898 (   job_applicantanswer_question_id_42db3805    INDEX     o   CREATE INDEX job_applicantanswer_question_id_42db3805 ON public.job_applicantanswer USING btree (question_id);
 <   DROP INDEX public.job_applicantanswer_question_id_42db3805;
       public            u2m65eq7rc7j8s    false    276                       1259    26133894    job_application_job_id_df862b7b    INDEX     ]   CREATE INDEX job_application_job_id_df862b7b ON public.job_application USING btree (job_id);
 3   DROP INDEX public.job_application_job_id_df862b7b;
       public            u2m65eq7rc7j8s    false    278                       1259    26133895     job_application_user_id_57c7fe2c    INDEX     _   CREATE INDEX job_application_user_id_57c7fe2c ON public.job_application USING btree (user_id);
 4   DROP INDEX public.job_application_user_id_57c7fe2c;
       public            u2m65eq7rc7j8s    false    278            6           1259    26133926 #   job_completedskills_job_id_b22ffa15    INDEX     e   CREATE INDEX job_completedskills_job_id_b22ffa15 ON public.job_completedskills USING btree (job_id);
 7   DROP INDEX public.job_completedskills_job_id_b22ffa15;
       public            u2m65eq7rc7j8s    false    292            9           1259    26133927 %   job_completedskills_skill_id_9bc5f590    INDEX     i   CREATE INDEX job_completedskills_skill_id_9bc5f590 ON public.job_completedskills USING btree (skill_id);
 9   DROP INDEX public.job_completedskills_skill_id_9bc5f590;
       public            u2m65eq7rc7j8s    false    292            :           1259    26133928 $   job_completedskills_user_id_032e2fc2    INDEX     g   CREATE INDEX job_completedskills_user_id_032e2fc2 ON public.job_completedskills USING btree (user_id);
 8   DROP INDEX public.job_completedskills_user_id_032e2fc2;
       public            u2m65eq7rc7j8s    false    292                       1259    26133863    job_job_category_id_555b6898    INDEX     W   CREATE INDEX job_job_category_id_555b6898 ON public.job_job USING btree (category_id);
 0   DROP INDEX public.job_job_category_id_555b6898;
       public            u2m65eq7rc7j8s    false    280                       1259    26133864    job_job_company_id_16c78d68    INDEX     U   CREATE INDEX job_job_company_id_16c78d68 ON public.job_job USING btree (company_id);
 /   DROP INDEX public.job_job_company_id_16c78d68;
       public            u2m65eq7rc7j8s    false    280            *           1259    26133877 (   job_job_extracted_skills_job_id_fb294cdb    INDEX     o   CREATE INDEX job_job_extracted_skills_job_id_fb294cdb ON public.job_job_extracted_skills USING btree (job_id);
 <   DROP INDEX public.job_job_extracted_skills_job_id_fb294cdb;
       public            u2m65eq7rc7j8s    false    288            /           1259    26133878 *   job_job_extracted_skills_skill_id_9a9d1045    INDEX     s   CREATE INDEX job_job_extracted_skills_skill_id_9a9d1045 ON public.job_job_extracted_skills USING btree (skill_id);
 >   DROP INDEX public.job_job_extracted_skills_skill_id_9a9d1045;
       public            u2m65eq7rc7j8s    false    288            0           1259    26133891 $   job_job_requirements_job_id_6dea1bff    INDEX     g   CREATE INDEX job_job_requirements_job_id_6dea1bff ON public.job_job_requirements USING btree (job_id);
 8   DROP INDEX public.job_job_requirements_job_id_6dea1bff;
       public            u2m65eq7rc7j8s    false    290            5           1259    26133892 &   job_job_requirements_skill_id_0c65076a    INDEX     k   CREATE INDEX job_job_requirements_skill_id_0c65076a ON public.job_job_requirements USING btree (skill_id);
 :   DROP INDEX public.job_job_requirements_skill_id_0c65076a;
       public            u2m65eq7rc7j8s    false    290                       1259    26133893    job_job_user_id_bab12bbc    INDEX     O   CREATE INDEX job_job_user_id_bab12bbc ON public.job_job USING btree (user_id);
 ,   DROP INDEX public.job_job_user_id_bab12bbc;
       public            u2m65eq7rc7j8s    false    280                       1259    26133862    job_mcq_job_title_id_6c3c88aa    INDEX     Y   CREATE INDEX job_mcq_job_title_id_6c3c88aa ON public.job_mcq USING btree (job_title_id);
 1   DROP INDEX public.job_mcq_job_title_id_6c3c88aa;
       public            u2m65eq7rc7j8s    false    282                        1259    26133794    job_savedjob_job_id_d6871938    INDEX     W   CREATE INDEX job_savedjob_job_id_d6871938 ON public.job_savedjob USING btree (job_id);
 0   DROP INDEX public.job_savedjob_job_id_d6871938;
       public            u2m65eq7rc7j8s    false    284            #           1259    26133861    job_savedjob_user_id_e04feb74    INDEX     Y   CREATE INDEX job_savedjob_user_id_e04feb74 ON public.job_savedjob USING btree (user_id);
 1   DROP INDEX public.job_savedjob_user_id_e04feb74;
       public            u2m65eq7rc7j8s    false    284            &           1259    26133955 !   job_skillquestion_job_id_0e5c3356    INDEX     a   CREATE INDEX job_skillquestion_job_id_0e5c3356 ON public.job_skillquestion USING btree (job_id);
 5   DROP INDEX public.job_skillquestion_job_id_0e5c3356;
       public            u2m65eq7rc7j8s    false    286            )           1259    26133793 #   job_skillquestion_skill_id_ae322e71    INDEX     e   CREATE INDEX job_skillquestion_skill_id_ae322e71 ON public.job_skillquestion USING btree (skill_id);
 7   DROP INDEX public.job_skillquestion_skill_id_ae322e71;
       public            u2m65eq7rc7j8s    false    286            A           1259    26133998 .   messaging_chatmessage_conversation_id_e02f8ad8    INDEX     {   CREATE INDEX messaging_chatmessage_conversation_id_e02f8ad8 ON public.messaging_chatmessage USING btree (conversation_id);
 B   DROP INDEX public.messaging_chatmessage_conversation_id_e02f8ad8;
       public            u2m65eq7rc7j8s    false    296            D           1259    26133999 (   messaging_chatmessage_sender_id_9dffc4f6    INDEX     o   CREATE INDEX messaging_chatmessage_sender_id_9dffc4f6 ON public.messaging_chatmessage USING btree (sender_id);
 <   DROP INDEX public.messaging_chatmessage_sender_id_9dffc4f6;
       public            u2m65eq7rc7j8s    false    296            =           1259    26133986 /   messaging_conversation_participant1_id_2e70a199    INDEX     }   CREATE INDEX messaging_conversation_participant1_id_2e70a199 ON public.messaging_conversation USING btree (participant1_id);
 C   DROP INDEX public.messaging_conversation_participant1_id_2e70a199;
       public            u2m65eq7rc7j8s    false    294            >           1259    26133987 /   messaging_conversation_participant2_id_df0800d0    INDEX     }   CREATE INDEX messaging_conversation_participant2_id_df0800d0 ON public.messaging_conversation USING btree (participant2_id);
 C   DROP INDEX public.messaging_conversation_participant2_id_df0800d0;
       public            u2m65eq7rc7j8s    false    294            G           1259    26134013 +   notifications_notification_user_id_b5e8c0ff    INDEX     u   CREATE INDEX notifications_notification_user_id_b5e8c0ff ON public.notifications_notification USING btree (user_id);
 ?   DROP INDEX public.notifications_notification_user_id_b5e8c0ff;
       public            u2m65eq7rc7j8s    false    298            J           1259    26134055 6   onboarding_generalknowledgeanswer_question_id_bcc63298    INDEX     �   CREATE INDEX onboarding_generalknowledgeanswer_question_id_bcc63298 ON public.onboarding_generalknowledgeanswer USING btree (question_id);
 J   DROP INDEX public.onboarding_generalknowledgeanswer_question_id_bcc63298;
       public            u2m65eq7rc7j8s    false    300            M           1259    26134042 *   onboarding_quizresponse_answer_id_dc07be57    INDEX     s   CREATE INDEX onboarding_quizresponse_answer_id_dc07be57 ON public.onboarding_quizresponse USING btree (answer_id);
 >   DROP INDEX public.onboarding_quizresponse_answer_id_dc07be57;
       public            u2m65eq7rc7j8s    false    304            N           1259    26134043 /   onboarding_quizresponse_application_id_d065f039    INDEX     }   CREATE INDEX onboarding_quizresponse_application_id_d065f039 ON public.onboarding_quizresponse USING btree (application_id);
 C   DROP INDEX public.onboarding_quizresponse_application_id_d065f039;
       public            u2m65eq7rc7j8s    false    304            Q           1259    26134054 *   onboarding_quizresponse_resume_id_13ff220f    INDEX     s   CREATE INDEX onboarding_quizresponse_resume_id_13ff220f ON public.onboarding_quizresponse USING btree (resume_id);
 >   DROP INDEX public.onboarding_quizresponse_resume_id_13ff220f;
       public            u2m65eq7rc7j8s    false    304            
           1259    26134065 (   resume_contactinfo_job_title_id_242c128c    INDEX     o   CREATE INDEX resume_contactinfo_job_title_id_242c128c ON public.resume_contactinfo USING btree (job_title_id);
 <   DROP INDEX public.resume_contactinfo_job_title_id_242c128c;
       public            u2m65eq7rc7j8s    false    274                       1259    26133711 #   resume_contactinfo_user_id_3b7b5c4b    INDEX     e   CREATE INDEX resume_contactinfo_user_id_3b7b5c4b ON public.resume_contactinfo USING btree (user_id);
 7   DROP INDEX public.resume_contactinfo_user_id_3b7b5c4b;
       public            u2m65eq7rc7j8s    false    274            �           1259    26133632 #   resume_education_resume_id_dfdfc5f8    INDEX     e   CREATE INDEX resume_education_resume_id_dfdfc5f8 ON public.resume_education USING btree (resume_id);
 7   DROP INDEX public.resume_education_resume_id_dfdfc5f8;
       public            u2m65eq7rc7j8s    false    254            �           1259    26133609 !   resume_education_user_id_f5d009fe    INDEX     a   CREATE INDEX resume_education_user_id_f5d009fe ON public.resume_education USING btree (user_id);
 5   DROP INDEX public.resume_education_user_id_f5d009fe;
       public            u2m65eq7rc7j8s    false    254            �           1259    26133639 $   resume_experience_resume_id_8800379b    INDEX     g   CREATE INDEX resume_experience_resume_id_8800379b ON public.resume_experience USING btree (resume_id);
 8   DROP INDEX public.resume_experience_resume_id_8800379b;
       public            u2m65eq7rc7j8s    false    256            �           1259    26133607 "   resume_experience_user_id_e5b1e321    INDEX     c   CREATE INDEX resume_experience_user_id_e5b1e321 ON public.resume_experience USING btree (user_id);
 6   DROP INDEX public.resume_experience_user_id_e5b1e321;
       public            u2m65eq7rc7j8s    false    256            �           1259    26133739 "   resume_resume_category_id_3b636544    INDEX     c   CREATE INDEX resume_resume_category_id_3b636544 ON public.resume_resume USING btree (category_id);
 6   DROP INDEX public.resume_resume_category_id_3b636544;
       public            u2m65eq7rc7j8s    false    258                       1259    26133624 '   resume_resume_skills_resume_id_578fac8e    INDEX     m   CREATE INDEX resume_resume_skills_resume_id_578fac8e ON public.resume_resume_skills USING btree (resume_id);
 ;   DROP INDEX public.resume_resume_skills_resume_id_578fac8e;
       public            u2m65eq7rc7j8s    false    270                       1259    26133605 &   resume_resume_skills_skill_id_8c254c49    INDEX     k   CREATE INDEX resume_resume_skills_skill_id_8c254c49 ON public.resume_resume_skills USING btree (skill_id);
 :   DROP INDEX public.resume_resume_skills_skill_id_8c254c49;
       public            u2m65eq7rc7j8s    false    270            �           1259    26133674 7   resume_resumedoc_extracted_skills_resumedoc_id_0137a39a    INDEX     �   CREATE INDEX resume_resumedoc_extracted_skills_resumedoc_id_0137a39a ON public.resume_resumedoc_extracted_skills USING btree (resumedoc_id);
 K   DROP INDEX public.resume_resumedoc_extracted_skills_resumedoc_id_0137a39a;
       public            u2m65eq7rc7j8s    false    268            �           1259    26133543 3   resume_resumedoc_extracted_skills_skill_id_87b52453    INDEX     �   CREATE INDEX resume_resumedoc_extracted_skills_skill_id_87b52453 ON public.resume_resumedoc_extracted_skills USING btree (skill_id);
 G   DROP INDEX public.resume_resumedoc_extracted_skills_skill_id_87b52453;
       public            u2m65eq7rc7j8s    false    268            �           1259    26133528 )   resume_skill_categories_skill_id_f7624fe7    INDEX     q   CREATE INDEX resume_skill_categories_skill_id_f7624fe7 ON public.resume_skill_categories USING btree (skill_id);
 =   DROP INDEX public.resume_skill_categories_skill_id_f7624fe7;
       public            u2m65eq7rc7j8s    false    264            �           1259    26133529 1   resume_skill_categories_skillcategory_id_136196cd    INDEX     �   CREATE INDEX resume_skill_categories_skillcategory_id_136196cd ON public.resume_skill_categories USING btree (skillcategory_id);
 E   DROP INDEX public.resume_skill_categories_skillcategory_id_136196cd;
       public            u2m65eq7rc7j8s    false    264            �           1259    26133732    resume_skill_user_id_689dedef    INDEX     Y   CREATE INDEX resume_skill_user_id_689dedef ON public.resume_skill USING btree (user_id);
 1   DROP INDEX public.resume_skill_user_id_689dedef;
       public            u2m65eq7rc7j8s    false    262            X           1259    26134131 (   resume_userlanguage_language_id_ccb1d683    INDEX     o   CREATE INDEX resume_userlanguage_language_id_ccb1d683 ON public.resume_userlanguage USING btree (language_id);
 <   DROP INDEX public.resume_userlanguage_language_id_ccb1d683;
       public            u2m65eq7rc7j8s    false    310            [           1259    26134132 ,   resume_userlanguage_user_profile_id_9ac84f21    INDEX     w   CREATE INDEX resume_userlanguage_user_profile_id_9ac84f21 ON public.resume_userlanguage USING btree (user_profile_id);
 @   DROP INDEX public.resume_userlanguage_user_profile_id_9ac84f21;
       public            u2m65eq7rc7j8s    false    310                       1259    26133723 (   resume_workexperience_resume_id_64f9c63e    INDEX     o   CREATE INDEX resume_workexperience_resume_id_64f9c63e ON public.resume_workexperience USING btree (resume_id);
 <   DROP INDEX public.resume_workexperience_resume_id_64f9c63e;
       public            u2m65eq7rc7j8s    false    272            	           1259    26133705 &   resume_workexperience_user_id_fbba1b93    INDEX     k   CREATE INDEX resume_workexperience_user_id_fbba1b93 ON public.resume_workexperience USING btree (user_id);
 :   DROP INDEX public.resume_workexperience_user_id_fbba1b93;
       public            u2m65eq7rc7j8s    false    272            i           1259    26134203    social_auth_code_code_a2393167    INDEX     [   CREATE INDEX social_auth_code_code_a2393167 ON public.social_auth_code USING btree (code);
 2   DROP INDEX public.social_auth_code_code_a2393167;
       public            u2m65eq7rc7j8s    false    317            j           1259    26134204 #   social_auth_code_code_a2393167_like    INDEX     t   CREATE INDEX social_auth_code_code_a2393167_like ON public.social_auth_code USING btree (code varchar_pattern_ops);
 7   DROP INDEX public.social_auth_code_code_a2393167_like;
       public            u2m65eq7rc7j8s    false    317            o           1259    26134228 #   social_auth_code_timestamp_176b341f    INDEX     g   CREATE INDEX social_auth_code_timestamp_176b341f ON public.social_auth_code USING btree ("timestamp");
 7   DROP INDEX public.social_auth_code_timestamp_176b341f;
       public            u2m65eq7rc7j8s    false    317            }           1259    26134230 &   social_auth_partial_timestamp_50f2119f    INDEX     m   CREATE INDEX social_auth_partial_timestamp_50f2119f ON public.social_auth_partial USING btree ("timestamp");
 :   DROP INDEX public.social_auth_partial_timestamp_50f2119f;
       public            u2m65eq7rc7j8s    false    323            ~           1259    26134225 "   social_auth_partial_token_3017fea3    INDEX     c   CREATE INDEX social_auth_partial_token_3017fea3 ON public.social_auth_partial USING btree (token);
 6   DROP INDEX public.social_auth_partial_token_3017fea3;
       public            u2m65eq7rc7j8s    false    323                       1259    26134226 '   social_auth_partial_token_3017fea3_like    INDEX     |   CREATE INDEX social_auth_partial_token_3017fea3_like ON public.social_auth_partial USING btree (token varchar_pattern_ops);
 ;   DROP INDEX public.social_auth_partial_token_3017fea3_like;
       public            u2m65eq7rc7j8s    false    323            x           1259    26134233 '   social_auth_usersocialauth_uid_796e51dc    INDEX     m   CREATE INDEX social_auth_usersocialauth_uid_796e51dc ON public.social_auth_usersocialauth USING btree (uid);
 ;   DROP INDEX public.social_auth_usersocialauth_uid_796e51dc;
       public            u2m65eq7rc7j8s    false    321            y           1259    26134234 ,   social_auth_usersocialauth_uid_796e51dc_like    INDEX     �   CREATE INDEX social_auth_usersocialauth_uid_796e51dc_like ON public.social_auth_usersocialauth USING btree (uid varchar_pattern_ops);
 @   DROP INDEX public.social_auth_usersocialauth_uid_796e51dc_like;
       public            u2m65eq7rc7j8s    false    321            z           1259    26134210 +   social_auth_usersocialauth_user_id_17d28448    INDEX     u   CREATE INDEX social_auth_usersocialauth_user_id_17d28448 ON public.social_auth_usersocialauth USING btree (user_id);
 ?   DROP INDEX public.social_auth_usersocialauth_user_id_17d28448;
       public            u2m65eq7rc7j8s    false    321            �           1259    26134404 (   social_features_comment_post_id_02df961f    INDEX     o   CREATE INDEX social_features_comment_post_id_02df961f ON public.social_features_comment USING btree (post_id);
 <   DROP INDEX public.social_features_comment_post_id_02df961f;
       public            u2m65eq7rc7j8s    false    333            �           1259    26134405 (   social_features_comment_user_id_675fed60    INDEX     o   CREATE INDEX social_features_comment_user_id_675fed60 ON public.social_features_comment USING btree (user_id);
 <   DROP INDEX public.social_features_comment_user_id_675fed60;
       public            u2m65eq7rc7j8s    false    333            �           1259    26134392 +   social_features_follow_followed_id_bdbc53f2    INDEX     u   CREATE INDEX social_features_follow_followed_id_bdbc53f2 ON public.social_features_follow USING btree (followed_id);
 ?   DROP INDEX public.social_features_follow_followed_id_bdbc53f2;
       public            u2m65eq7rc7j8s    false    331            �           1259    26134393 +   social_features_follow_follower_id_dc6192e1    INDEX     u   CREATE INDEX social_features_follow_follower_id_dc6192e1 ON public.social_features_follow USING btree (follower_id);
 ?   DROP INDEX public.social_features_follow_follower_id_dc6192e1;
       public            u2m65eq7rc7j8s    false    331            �           1259    26134380 %   social_features_like_post_id_f8c78122    INDEX     i   CREATE INDEX social_features_like_post_id_f8c78122 ON public.social_features_like USING btree (post_id);
 9   DROP INDEX public.social_features_like_post_id_f8c78122;
       public            u2m65eq7rc7j8s    false    329            �           1259    26134381 %   social_features_like_user_id_54e40bc3    INDEX     i   CREATE INDEX social_features_like_user_id_54e40bc3 ON public.social_features_like USING btree (user_id);
 9   DROP INDEX public.social_features_like_user_id_54e40bc3;
       public            u2m65eq7rc7j8s    false    329            �           1259    26134326 -   social_features_message_recipient_id_f3681f33    INDEX     y   CREATE INDEX social_features_message_recipient_id_f3681f33 ON public.social_features_message USING btree (recipient_id);
 A   DROP INDEX public.social_features_message_recipient_id_f3681f33;
       public            u2m65eq7rc7j8s    false    325            �           1259    26134327 *   social_features_message_sender_id_5d2bb113    INDEX     s   CREATE INDEX social_features_message_sender_id_5d2bb113 ON public.social_features_message USING btree (sender_id);
 >   DROP INDEX public.social_features_message_sender_id_5d2bb113;
       public            u2m65eq7rc7j8s    false    325            �           1259    26134364 '   social_features_post_author_id_b04d5c3c    INDEX     m   CREATE INDEX social_features_post_author_id_b04d5c3c ON public.social_features_post USING btree (author_id);
 ;   DROP INDEX public.social_features_post_author_id_b04d5c3c;
       public            u2m65eq7rc7j8s    false    324            �           1259    26134443 ,   socialaccount_socialaccount_user_id_8146e70c    INDEX     w   CREATE INDEX socialaccount_socialaccount_user_id_8146e70c ON public.socialaccount_socialaccount USING btree (user_id);
 @   DROP INDEX public.socialaccount_socialaccount_user_id_8146e70c;
       public            u2m65eq7rc7j8s    false    335            �           1259    26134457 .   socialaccount_socialapp_sites_site_id_2579dee5    INDEX     {   CREATE INDEX socialaccount_socialapp_sites_site_id_2579dee5 ON public.socialaccount_socialapp_sites USING btree (site_id);
 B   DROP INDEX public.socialaccount_socialapp_sites_site_id_2579dee5;
       public            u2m65eq7rc7j8s    false    339            �           1259    26134456 3   socialaccount_socialapp_sites_socialapp_id_97fb6e7d    INDEX     �   CREATE INDEX socialaccount_socialapp_sites_socialapp_id_97fb6e7d ON public.socialaccount_socialapp_sites USING btree (socialapp_id);
 G   DROP INDEX public.socialaccount_socialapp_sites_socialapp_id_97fb6e7d;
       public            u2m65eq7rc7j8s    false    339            �           1259    26134468 -   socialaccount_socialtoken_account_id_951f210e    INDEX     y   CREATE INDEX socialaccount_socialtoken_account_id_951f210e ON public.socialaccount_socialtoken USING btree (account_id);
 A   DROP INDEX public.socialaccount_socialtoken_account_id_951f210e;
       public            u2m65eq7rc7j8s    false    341            �           1259    26134469 )   socialaccount_socialtoken_app_id_636a42d7    INDEX     q   CREATE INDEX socialaccount_socialtoken_app_id_636a42d7 ON public.socialaccount_socialtoken USING btree (app_id);
 =   DROP INDEX public.socialaccount_socialtoken_app_id_636a42d7;
       public            u2m65eq7rc7j8s    false    341            �           1259    26133334    unique_verified_email    INDEX     m   CREATE UNIQUE INDEX unique_verified_email ON public.account_emailaddress USING btree (email) WHERE verified;
 )   DROP INDEX public.unique_verified_email;
       public            u2m65eq7rc7j8s    false    236    236            �           1259    26133270    users_user_email_243f6e77_like    INDEX     j   CREATE INDEX users_user_email_243f6e77_like ON public.users_user USING btree (email varchar_pattern_ops);
 2   DROP INDEX public.users_user_email_243f6e77_like;
       public            u2m65eq7rc7j8s    false    230            �           1259    26133284 #   users_user_groups_group_id_9afc8d0e    INDEX     e   CREATE INDEX users_user_groups_group_id_9afc8d0e ON public.users_user_groups USING btree (group_id);
 7   DROP INDEX public.users_user_groups_group_id_9afc8d0e;
       public            u2m65eq7rc7j8s    false    232            �           1259    26133283 "   users_user_groups_user_id_5f6f5a90    INDEX     c   CREATE INDEX users_user_groups_user_id_5f6f5a90 ON public.users_user_groups USING btree (user_id);
 6   DROP INDEX public.users_user_groups_user_id_5f6f5a90;
       public            u2m65eq7rc7j8s    false    232            �           1259    26133298 2   users_user_user_permissions_permission_id_0b93982e    INDEX     �   CREATE INDEX users_user_user_permissions_permission_id_0b93982e ON public.users_user_user_permissions USING btree (permission_id);
 F   DROP INDEX public.users_user_user_permissions_permission_id_0b93982e;
       public            u2m65eq7rc7j8s    false    234            �           1259    26133297 ,   users_user_user_permissions_user_id_20aca447    INDEX     w   CREATE INDEX users_user_user_permissions_user_id_20aca447 ON public.users_user_user_permissions USING btree (user_id);
 @   DROP INDEX public.users_user_user_permissions_user_id_20aca447;
       public            u2m65eq7rc7j8s    false    234            �           1259    26133269 !   users_user_username_06e46fe6_like    INDEX     p   CREATE INDEX users_user_username_06e46fe6_like ON public.users_user USING btree (username varchar_pattern_ops);
 5   DROP INDEX public.users_user_username_06e46fe6_like;
       public            u2m65eq7rc7j8s    false    230            �           2606    26133315 K   account_emailaddress account_emailaddress_user_id_2c513194_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.account_emailaddress
    ADD CONSTRAINT account_emailaddress_user_id_2c513194_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.account_emailaddress DROP CONSTRAINT account_emailaddress_user_id_2c513194_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    236    230            �           2606    26133322 U   account_emailconfirmation account_emailconfirm_email_address_id_5b7f8c58_fk_account_e    FK CONSTRAINT     �   ALTER TABLE ONLY public.account_emailconfirmation
    ADD CONSTRAINT account_emailconfirm_email_address_id_5b7f8c58_fk_account_e FOREIGN KEY (email_address_id) REFERENCES public.account_emailaddress(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.account_emailconfirmation DROP CONSTRAINT account_emailconfirm_email_address_id_5b7f8c58_fk_account_e;
       public          u2m65eq7rc7j8s    false    236    238    4537            �           2606    26133424 I   asseessments_option asseessments_option_question_id_cc527d25_fk_asseessme    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_option
    ADD CONSTRAINT asseessments_option_question_id_cc527d25_fk_asseessme FOREIGN KEY (question_id) REFERENCES public.asseessments_question(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.asseessments_option DROP CONSTRAINT asseessments_option_question_id_cc527d25_fk_asseessme;
       public          u2m65eq7rc7j8s    false    246    4560    244            �           2606    26133419 N   asseessments_question asseessments_questio_assessment_id_421d6d70_fk_asseessme    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_question
    ADD CONSTRAINT asseessments_questio_assessment_id_421d6d70_fk_asseessme FOREIGN KEY (assessment_id) REFERENCES public.asseessments_assessment(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.asseessments_question DROP CONSTRAINT asseessments_questio_assessment_id_421d6d70_fk_asseessme;
       public          u2m65eq7rc7j8s    false    246    242    4554                        2606    26133404 I   asseessments_result asseessments_result_question_id_4f643745_fk_asseessme    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_result
    ADD CONSTRAINT asseessments_result_question_id_4f643745_fk_asseessme FOREIGN KEY (question_id) REFERENCES public.asseessments_question(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.asseessments_result DROP CONSTRAINT asseessments_result_question_id_4f643745_fk_asseessme;
       public          u2m65eq7rc7j8s    false    248    4560    246                       2606    26133409 P   asseessments_result asseessments_result_selected_option_id_5bc3c3c3_fk_asseessme    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_result
    ADD CONSTRAINT asseessments_result_selected_option_id_5bc3c3c3_fk_asseessme FOREIGN KEY (selected_option_id) REFERENCES public.asseessments_option(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.asseessments_result DROP CONSTRAINT asseessments_result_selected_option_id_5bc3c3c3_fk_asseessme;
       public          u2m65eq7rc7j8s    false    4556    244    248                       2606    26133414 H   asseessments_result asseessments_result_session_id_3c5fd623_fk_asseessme    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_result
    ADD CONSTRAINT asseessments_result_session_id_3c5fd623_fk_asseessme FOREIGN KEY (session_id) REFERENCES public.asseessments_session(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.asseessments_result DROP CONSTRAINT asseessments_result_session_id_3c5fd623_fk_asseessme;
       public          u2m65eq7rc7j8s    false    248    250    4568                       2606    26133393 M   asseessments_session asseessments_session_assessment_id_22cebda1_fk_asseessme    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_session
    ADD CONSTRAINT asseessments_session_assessment_id_22cebda1_fk_asseessme FOREIGN KEY (assessment_id) REFERENCES public.asseessments_assessment(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.asseessments_session DROP CONSTRAINT asseessments_session_assessment_id_22cebda1_fk_asseessme;
       public          u2m65eq7rc7j8s    false    242    250    4554                       2606    26133399 K   asseessments_session asseessments_session_user_id_3909b917_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.asseessments_session
    ADD CONSTRAINT asseessments_session_user_id_3909b917_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.asseessments_session DROP CONSTRAINT asseessments_session_user_id_3909b917_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    4520    250            �           2606    26133235 O   auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
       public          u2m65eq7rc7j8s    false    228    4504    224            �           2606    26133230 P   auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
       public          u2m65eq7rc7j8s    false    4509    226    228            �           2606    26133221 E   auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co;
       public          u2m65eq7rc7j8s    false    4499    224    222            J           2606    28295581 D   cities_light_city cities_light_city_country_id_cf310fd2_fk_cities_li    FK CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_country_id_cf310fd2_fk_cities_li FOREIGN KEY (country_id) REFERENCES public.cities_light_country(id) DEFERRABLE INITIALLY DEFERRED;
 n   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_country_id_cf310fd2_fk_cities_li;
       public          u2m65eq7rc7j8s    false    343    4793    347            K           2606    28295576 P   cities_light_city cities_light_city_region_id_f7ab977b_fk_cities_light_region_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_region_id_f7ab977b_fk_cities_light_region_id FOREIGN KEY (region_id) REFERENCES public.cities_light_region(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_region_id_f7ab977b_fk_cities_light_region_id;
       public          u2m65eq7rc7j8s    false    345    4812    347            L           2606    28295610 F   cities_light_city cities_light_city_subregion_id_0926d2ad_fk_cities_li    FK CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_city
    ADD CONSTRAINT cities_light_city_subregion_id_0926d2ad_fk_cities_li FOREIGN KEY (subregion_id) REFERENCES public.cities_light_subregion(id) DEFERRABLE INITIALLY DEFERRED;
 p   ALTER TABLE ONLY public.cities_light_city DROP CONSTRAINT cities_light_city_subregion_id_0926d2ad_fk_cities_li;
       public          u2m65eq7rc7j8s    false    347    4847    349            I           2606    28295546 H   cities_light_region cities_light_region_country_id_b2782d49_fk_cities_li    FK CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_region
    ADD CONSTRAINT cities_light_region_country_id_b2782d49_fk_cities_li FOREIGN KEY (country_id) REFERENCES public.cities_light_country(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.cities_light_region DROP CONSTRAINT cities_light_region_country_id_b2782d49_fk_cities_li;
       public          u2m65eq7rc7j8s    false    4793    343    345            M           2606    28295615 L   cities_light_subregion cities_light_subregi_country_id_9b32b484_fk_cities_li    FK CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_subregion
    ADD CONSTRAINT cities_light_subregi_country_id_9b32b484_fk_cities_li FOREIGN KEY (country_id) REFERENCES public.cities_light_country(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.cities_light_subregion DROP CONSTRAINT cities_light_subregi_country_id_9b32b484_fk_cities_li;
       public          u2m65eq7rc7j8s    false    349    343    4793            N           2606    28295640 K   cities_light_subregion cities_light_subregi_region_id_c6e0b71f_fk_cities_li    FK CONSTRAINT     �   ALTER TABLE ONLY public.cities_light_subregion
    ADD CONSTRAINT cities_light_subregi_region_id_c6e0b71f_fk_cities_li FOREIGN KEY (region_id) REFERENCES public.cities_light_region(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.cities_light_subregion DROP CONSTRAINT cities_light_subregi_region_id_c6e0b71f_fk_cities_li;
       public          u2m65eq7rc7j8s    false    4812    349    345                       2606    26133444 A   company_company company_company_user_id_c99db68c_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.company_company
    ADD CONSTRAINT company_company_user_id_c99db68c_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 k   ALTER TABLE ONLY public.company_company DROP CONSTRAINT company_company_user_id_c99db68c_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    252    4520            �           2606    26133345 G   django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co;
       public          u2m65eq7rc7j8s    false    222    4499    240            �           2606    26133350 C   django_admin_log django_admin_log_user_id_c564eba6_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 m   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    4520    240                       2606    26133844 N   job_applicantanswer job_applicantanswer_applicant_id_237a7f43_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_applicantanswer
    ADD CONSTRAINT job_applicantanswer_applicant_id_237a7f43_fk_users_user_id FOREIGN KEY (applicant_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.job_applicantanswer DROP CONSTRAINT job_applicantanswer_applicant_id_237a7f43_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    276    230    4520                       2606    26133956 L   job_applicantanswer job_applicantanswer_application_id_b8401d6a_fk_job_appli    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_applicantanswer
    ADD CONSTRAINT job_applicantanswer_application_id_b8401d6a_fk_job_appli FOREIGN KEY (application_id) REFERENCES public.job_application(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.job_applicantanswer DROP CONSTRAINT job_applicantanswer_application_id_b8401d6a_fk_job_appli;
       public          u2m65eq7rc7j8s    false    278    4630    276                       2606    26133849 E   job_applicantanswer job_applicantanswer_job_id_ed8cef68_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_applicantanswer
    ADD CONSTRAINT job_applicantanswer_job_id_ed8cef68_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.job_applicantanswer DROP CONSTRAINT job_applicantanswer_job_id_ed8cef68_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    280    4635    276                       2606    26133854 I   job_applicantanswer job_applicantanswer_question_id_42db3805_fk_job_skill    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_applicantanswer
    ADD CONSTRAINT job_applicantanswer_question_id_42db3805_fk_job_skill FOREIGN KEY (question_id) REFERENCES public.job_skillquestion(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.job_applicantanswer DROP CONSTRAINT job_applicantanswer_question_id_42db3805_fk_job_skill;
       public          u2m65eq7rc7j8s    false    4648    286    276                       2606    26133939 =   job_application job_application_job_id_df862b7b_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_application
    ADD CONSTRAINT job_application_job_id_df862b7b_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 g   ALTER TABLE ONLY public.job_application DROP CONSTRAINT job_application_job_id_df862b7b_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    4635    280    278                       2606    26133839 A   job_application job_application_user_id_57c7fe2c_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_application
    ADD CONSTRAINT job_application_user_id_57c7fe2c_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 k   ALTER TABLE ONLY public.job_application DROP CONSTRAINT job_application_user_id_57c7fe2c_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    278    230    4520            *           2606    26133911 E   job_completedskills job_completedskills_job_id_b22ffa15_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_completedskills
    ADD CONSTRAINT job_completedskills_job_id_b22ffa15_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.job_completedskills DROP CONSTRAINT job_completedskills_job_id_b22ffa15_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    4635    280    292            +           2606    26133916 L   job_completedskills job_completedskills_skill_id_9bc5f590_fk_resume_skill_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_completedskills
    ADD CONSTRAINT job_completedskills_skill_id_9bc5f590_fk_resume_skill_id FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.job_completedskills DROP CONSTRAINT job_completedskills_skill_id_9bc5f590_fk_resume_skill_id;
       public          u2m65eq7rc7j8s    false    262    292    4590            ,           2606    26133921 I   job_completedskills job_completedskills_user_id_032e2fc2_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_completedskills
    ADD CONSTRAINT job_completedskills_user_id_032e2fc2_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.job_completedskills DROP CONSTRAINT job_completedskills_user_id_032e2fc2_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    292    230                       2606    26133806 ?   job_job job_job_category_id_555b6898_fk_resume_skillcategory_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job
    ADD CONSTRAINT job_job_category_id_555b6898_fk_resume_skillcategory_id FOREIGN KEY (category_id) REFERENCES public.resume_skillcategory(id) DEFERRABLE INITIALLY DEFERRED;
 i   ALTER TABLE ONLY public.job_job DROP CONSTRAINT job_job_category_id_555b6898_fk_resume_skillcategory_id;
       public          u2m65eq7rc7j8s    false    260    4588    280                       2606    26133811 9   job_job job_job_company_id_16c78d68_fk_company_company_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job
    ADD CONSTRAINT job_job_company_id_16c78d68_fk_company_company_id FOREIGN KEY (company_id) REFERENCES public.company_company(id) DEFERRABLE INITIALLY DEFERRED;
 c   ALTER TABLE ONLY public.job_job DROP CONSTRAINT job_job_company_id_16c78d68_fk_company_company_id;
       public          u2m65eq7rc7j8s    false    252    280    4571            &           2606    26133867 O   job_job_extracted_skills job_job_extracted_skills_job_id_fb294cdb_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job_extracted_skills
    ADD CONSTRAINT job_job_extracted_skills_job_id_fb294cdb_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.job_job_extracted_skills DROP CONSTRAINT job_job_extracted_skills_job_id_fb294cdb_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    280    288    4635            '           2606    26133872 V   job_job_extracted_skills job_job_extracted_skills_skill_id_9a9d1045_fk_resume_skill_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job_extracted_skills
    ADD CONSTRAINT job_job_extracted_skills_skill_id_9a9d1045_fk_resume_skill_id FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.job_job_extracted_skills DROP CONSTRAINT job_job_extracted_skills_skill_id_9a9d1045_fk_resume_skill_id;
       public          u2m65eq7rc7j8s    false    4590    288    262            (           2606    26133881 G   job_job_requirements job_job_requirements_job_id_6dea1bff_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job_requirements
    ADD CONSTRAINT job_job_requirements_job_id_6dea1bff_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.job_job_requirements DROP CONSTRAINT job_job_requirements_job_id_6dea1bff_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    280    4635    290            )           2606    26133886 N   job_job_requirements job_job_requirements_skill_id_0c65076a_fk_resume_skill_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job_requirements
    ADD CONSTRAINT job_job_requirements_skill_id_0c65076a_fk_resume_skill_id FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.job_job_requirements DROP CONSTRAINT job_job_requirements_skill_id_0c65076a_fk_resume_skill_id;
       public          u2m65eq7rc7j8s    false    262    290    4590                        2606    26133828 1   job_job job_job_user_id_bab12bbc_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_job
    ADD CONSTRAINT job_job_user_id_bab12bbc_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 [   ALTER TABLE ONLY public.job_job DROP CONSTRAINT job_job_user_id_bab12bbc_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    280    4520    230            !           2606    26133800 @   job_mcq job_mcq_job_title_id_6c3c88aa_fk_resume_skillcategory_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_mcq
    ADD CONSTRAINT job_mcq_job_title_id_6c3c88aa_fk_resume_skillcategory_id FOREIGN KEY (job_title_id) REFERENCES public.resume_skillcategory(id) DEFERRABLE INITIALLY DEFERRED;
 j   ALTER TABLE ONLY public.job_mcq DROP CONSTRAINT job_mcq_job_title_id_6c3c88aa_fk_resume_skillcategory_id;
       public          u2m65eq7rc7j8s    false    260    4588    282            "           2606    26133788 7   job_savedjob job_savedjob_job_id_d6871938_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_savedjob
    ADD CONSTRAINT job_savedjob_job_id_d6871938_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 a   ALTER TABLE ONLY public.job_savedjob DROP CONSTRAINT job_savedjob_job_id_d6871938_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    284    280    4635            #           2606    26133795 ;   job_savedjob job_savedjob_user_id_e04feb74_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_savedjob
    ADD CONSTRAINT job_savedjob_user_id_e04feb74_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 e   ALTER TABLE ONLY public.job_savedjob DROP CONSTRAINT job_savedjob_user_id_e04feb74_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    284    230    4520            $           2606    26133950 A   job_skillquestion job_skillquestion_job_id_0e5c3356_fk_job_job_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_skillquestion
    ADD CONSTRAINT job_skillquestion_job_id_0e5c3356_fk_job_job_id FOREIGN KEY (job_id) REFERENCES public.job_job(id) DEFERRABLE INITIALLY DEFERRED;
 k   ALTER TABLE ONLY public.job_skillquestion DROP CONSTRAINT job_skillquestion_job_id_0e5c3356_fk_job_job_id;
       public          u2m65eq7rc7j8s    false    280    4635    286            %           2606    26133783 H   job_skillquestion job_skillquestion_skill_id_ae322e71_fk_resume_skill_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.job_skillquestion
    ADD CONSTRAINT job_skillquestion_skill_id_ae322e71_fk_resume_skill_id FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.job_skillquestion DROP CONSTRAINT job_skillquestion_skill_id_ae322e71_fk_resume_skill_id;
       public          u2m65eq7rc7j8s    false    286    262    4590            /           2606    26133988 P   messaging_chatmessage messaging_chatmessag_conversation_id_e02f8ad8_fk_messaging    FK CONSTRAINT     �   ALTER TABLE ONLY public.messaging_chatmessage
    ADD CONSTRAINT messaging_chatmessag_conversation_id_e02f8ad8_fk_messaging FOREIGN KEY (conversation_id) REFERENCES public.messaging_conversation(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.messaging_chatmessage DROP CONSTRAINT messaging_chatmessag_conversation_id_e02f8ad8_fk_messaging;
       public          u2m65eq7rc7j8s    false    296    294    4672            0           2606    26133993 O   messaging_chatmessage messaging_chatmessage_sender_id_9dffc4f6_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.messaging_chatmessage
    ADD CONSTRAINT messaging_chatmessage_sender_id_9dffc4f6_fk_users_user_id FOREIGN KEY (sender_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.messaging_chatmessage DROP CONSTRAINT messaging_chatmessage_sender_id_9dffc4f6_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    296    4520            -           2606    26133976 Q   messaging_conversation messaging_conversati_participant1_id_2e70a199_fk_users_use    FK CONSTRAINT     �   ALTER TABLE ONLY public.messaging_conversation
    ADD CONSTRAINT messaging_conversati_participant1_id_2e70a199_fk_users_use FOREIGN KEY (participant1_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.messaging_conversation DROP CONSTRAINT messaging_conversati_participant1_id_2e70a199_fk_users_use;
       public          u2m65eq7rc7j8s    false    4520    294    230            .           2606    26133981 Q   messaging_conversation messaging_conversati_participant2_id_df0800d0_fk_users_use    FK CONSTRAINT     �   ALTER TABLE ONLY public.messaging_conversation
    ADD CONSTRAINT messaging_conversati_participant2_id_df0800d0_fk_users_use FOREIGN KEY (participant2_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.messaging_conversation DROP CONSTRAINT messaging_conversati_participant2_id_df0800d0_fk_users_use;
       public          u2m65eq7rc7j8s    false    230    294    4520            1           2606    26134008 W   notifications_notification notifications_notification_user_id_b5e8c0ff_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.notifications_notification
    ADD CONSTRAINT notifications_notification_user_id_b5e8c0ff_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.notifications_notification DROP CONSTRAINT notifications_notification_user_id_b5e8c0ff_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    298    230            2           2606    26134049 X   onboarding_generalknowledgeanswer onboarding_generalkn_question_id_bcc63298_fk_onboardin    FK CONSTRAINT     �   ALTER TABLE ONLY public.onboarding_generalknowledgeanswer
    ADD CONSTRAINT onboarding_generalkn_question_id_bcc63298_fk_onboardin FOREIGN KEY (question_id) REFERENCES public.onboarding_generalknowledgequestion(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.onboarding_generalknowledgeanswer DROP CONSTRAINT onboarding_generalkn_question_id_bcc63298_fk_onboardin;
       public          u2m65eq7rc7j8s    false    4684    300    302            3           2606    26134032 L   onboarding_quizresponse onboarding_quizrespo_answer_id_dc07be57_fk_onboardin    FK CONSTRAINT     �   ALTER TABLE ONLY public.onboarding_quizresponse
    ADD CONSTRAINT onboarding_quizrespo_answer_id_dc07be57_fk_onboardin FOREIGN KEY (answer_id) REFERENCES public.onboarding_generalknowledgeanswer(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.onboarding_quizresponse DROP CONSTRAINT onboarding_quizrespo_answer_id_dc07be57_fk_onboardin;
       public          u2m65eq7rc7j8s    false    4681    304    300            4           2606    26134037 Q   onboarding_quizresponse onboarding_quizrespo_application_id_d065f039_fk_job_appli    FK CONSTRAINT     �   ALTER TABLE ONLY public.onboarding_quizresponse
    ADD CONSTRAINT onboarding_quizrespo_application_id_d065f039_fk_job_appli FOREIGN KEY (application_id) REFERENCES public.job_application(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.onboarding_quizresponse DROP CONSTRAINT onboarding_quizrespo_application_id_d065f039_fk_job_appli;
       public          u2m65eq7rc7j8s    false    4630    304    278            5           2606    26134044 V   onboarding_quizresponse onboarding_quizresponse_resume_id_13ff220f_fk_resume_resume_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.onboarding_quizresponse
    ADD CONSTRAINT onboarding_quizresponse_resume_id_13ff220f_fk_resume_resume_id FOREIGN KEY (resume_id) REFERENCES public.resume_resume(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.onboarding_quizresponse DROP CONSTRAINT onboarding_quizresponse_resume_id_13ff220f_fk_resume_resume_id;
       public          u2m65eq7rc7j8s    false    4584    304    258                       2606    26134066 H   resume_contactinfo resume_contactinfo_job_title_id_242c128c_fk_resume_sk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_contactinfo
    ADD CONSTRAINT resume_contactinfo_job_title_id_242c128c_fk_resume_sk FOREIGN KEY (job_title_id) REFERENCES public.resume_skillcategory(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.resume_contactinfo DROP CONSTRAINT resume_contactinfo_job_title_id_242c128c_fk_resume_sk;
       public          u2m65eq7rc7j8s    false    260    274    4588                       2606    26133706 G   resume_contactinfo resume_contactinfo_user_id_3b7b5c4b_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_contactinfo
    ADD CONSTRAINT resume_contactinfo_user_id_3b7b5c4b_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.resume_contactinfo DROP CONSTRAINT resume_contactinfo_user_id_3b7b5c4b_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    274    230                       2606    26133651 7   resume_education resume_education_resume_id_dfdfc5f8_fk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_education
    ADD CONSTRAINT resume_education_resume_id_dfdfc5f8_fk FOREIGN KEY (resume_id) REFERENCES public.resume_resume(id) DEFERRABLE INITIALLY DEFERRED;
 a   ALTER TABLE ONLY public.resume_education DROP CONSTRAINT resume_education_resume_id_dfdfc5f8_fk;
       public          u2m65eq7rc7j8s    false    258    4584    254                       2606    26133586 C   resume_education resume_education_user_id_f5d009fe_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_education
    ADD CONSTRAINT resume_education_user_id_f5d009fe_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 m   ALTER TABLE ONLY public.resume_education DROP CONSTRAINT resume_education_user_id_f5d009fe_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    4520    254                       2606    26133656 9   resume_experience resume_experience_resume_id_8800379b_fk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_experience
    ADD CONSTRAINT resume_experience_resume_id_8800379b_fk FOREIGN KEY (resume_id) REFERENCES public.resume_resume(id) DEFERRABLE INITIALLY DEFERRED;
 c   ALTER TABLE ONLY public.resume_experience DROP CONSTRAINT resume_experience_resume_id_8800379b_fk;
       public          u2m65eq7rc7j8s    false    256    4584    258            	           2606    26133576 E   resume_experience resume_experience_user_id_e5b1e321_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_experience
    ADD CONSTRAINT resume_experience_user_id_e5b1e321_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.resume_experience DROP CONSTRAINT resume_experience_user_id_e5b1e321_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    256    230            
           2606    26134146 K   resume_resume resume_resume_category_id_3b636544_fk_resume_skillcategory_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resume
    ADD CONSTRAINT resume_resume_category_id_3b636544_fk_resume_skillcategory_id FOREIGN KEY (category_id) REFERENCES public.resume_skillcategory(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.resume_resume DROP CONSTRAINT resume_resume_category_id_3b636544_fk_resume_skillcategory_id;
       public          u2m65eq7rc7j8s    false    4588    260    258                       2606    26133646 ?   resume_resume_skills resume_resume_skills_resume_id_578fac8e_fk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resume_skills
    ADD CONSTRAINT resume_resume_skills_resume_id_578fac8e_fk FOREIGN KEY (resume_id) REFERENCES public.resume_resume(id) DEFERRABLE INITIALLY DEFERRED;
 i   ALTER TABLE ONLY public.resume_resume_skills DROP CONSTRAINT resume_resume_skills_resume_id_578fac8e_fk;
       public          u2m65eq7rc7j8s    false    258    4584    270                       2606    26133599 N   resume_resume_skills resume_resume_skills_skill_id_8c254c49_fk_resume_skill_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resume_skills
    ADD CONSTRAINT resume_resume_skills_skill_id_8c254c49_fk_resume_skill_id FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.resume_resume_skills DROP CONSTRAINT resume_resume_skills_skill_id_8c254c49_fk_resume_skill_id;
       public          u2m65eq7rc7j8s    false    262    270    4590                       2606    26134141 =   resume_resume resume_resume_user_id_0b155703_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resume
    ADD CONSTRAINT resume_resume_user_id_0b155703_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 g   ALTER TABLE ONLY public.resume_resume DROP CONSTRAINT resume_resume_user_id_0b155703_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    230    258                       2606    26133537 U   resume_resumedoc_extracted_skills resume_resumedoc_ext_skill_id_87b52453_fk_resume_sk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills
    ADD CONSTRAINT resume_resumedoc_ext_skill_id_87b52453_fk_resume_sk FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.resume_resumedoc_extracted_skills DROP CONSTRAINT resume_resumedoc_ext_skill_id_87b52453_fk_resume_sk;
       public          u2m65eq7rc7j8s    false    262    4590    268                       2606    26133682 \   resume_resumedoc_extracted_skills resume_resumedoc_extracted_skills_resumedoc_id_0137a39a_fk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills
    ADD CONSTRAINT resume_resumedoc_extracted_skills_resumedoc_id_0137a39a_fk FOREIGN KEY (resumedoc_id) REFERENCES public.resume_resumedoc(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.resume_resumedoc_extracted_skills DROP CONSTRAINT resume_resumedoc_extracted_skills_resumedoc_id_0137a39a_fk;
       public          u2m65eq7rc7j8s    false    266    4599    268                       2606    26133546 C   resume_resumedoc resume_resumedoc_user_id_29199a99_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_resumedoc
    ADD CONSTRAINT resume_resumedoc_user_id_29199a99_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 m   ALTER TABLE ONLY public.resume_resumedoc DROP CONSTRAINT resume_resumedoc_user_id_29199a99_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    266    230    4520                       2606    26133523 S   resume_skill_categories resume_skill_categor_skillcategory_id_136196cd_fk_resume_sk    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_skill_categories
    ADD CONSTRAINT resume_skill_categor_skillcategory_id_136196cd_fk_resume_sk FOREIGN KEY (skillcategory_id) REFERENCES public.resume_skillcategory(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.resume_skill_categories DROP CONSTRAINT resume_skill_categor_skillcategory_id_136196cd_fk_resume_sk;
       public          u2m65eq7rc7j8s    false    4588    264    260                       2606    26133518 T   resume_skill_categories resume_skill_categories_skill_id_f7624fe7_fk_resume_skill_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_skill_categories
    ADD CONSTRAINT resume_skill_categories_skill_id_f7624fe7_fk_resume_skill_id FOREIGN KEY (skill_id) REFERENCES public.resume_skill(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.resume_skill_categories DROP CONSTRAINT resume_skill_categories_skill_id_f7624fe7_fk_resume_skill_id;
       public          u2m65eq7rc7j8s    false    4590    264    262                       2606    26133727 ;   resume_skill resume_skill_user_id_689dedef_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_skill
    ADD CONSTRAINT resume_skill_user_id_689dedef_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 e   ALTER TABLE ONLY public.resume_skill DROP CONSTRAINT resume_skill_user_id_689dedef_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    262    230    4520            7           2606    26134121 R   resume_userlanguage resume_userlanguage_language_id_ccb1d683_fk_resume_language_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_userlanguage
    ADD CONSTRAINT resume_userlanguage_language_id_ccb1d683_fk_resume_language_id FOREIGN KEY (language_id) REFERENCES public.resume_language(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.resume_userlanguage DROP CONSTRAINT resume_userlanguage_language_id_ccb1d683_fk_resume_language_id;
       public          u2m65eq7rc7j8s    false    308    4695    310            8           2606    26134126 M   resume_userlanguage resume_userlanguage_user_profile_id_9ac84f21_fk_resume_us    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_userlanguage
    ADD CONSTRAINT resume_userlanguage_user_profile_id_9ac84f21_fk_resume_us FOREIGN KEY (user_profile_id) REFERENCES public.resume_userprofile(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.resume_userlanguage DROP CONSTRAINT resume_userlanguage_user_profile_id_9ac84f21_fk_resume_us;
       public          u2m65eq7rc7j8s    false    4691    306    310            6           2606    26134079 G   resume_userprofile resume_userprofile_user_id_1ef1c095_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_userprofile
    ADD CONSTRAINT resume_userprofile_user_id_1ef1c095_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.resume_userprofile DROP CONSTRAINT resume_userprofile_user_id_1ef1c095_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    306    4520    230                       2606    26133713 R   resume_workexperience resume_workexperience_resume_id_64f9c63e_fk_resume_resume_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_workexperience
    ADD CONSTRAINT resume_workexperience_resume_id_64f9c63e_fk_resume_resume_id FOREIGN KEY (resume_id) REFERENCES public.resume_resume(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.resume_workexperience DROP CONSTRAINT resume_workexperience_resume_id_64f9c63e_fk_resume_resume_id;
       public          u2m65eq7rc7j8s    false    258    4584    272                       2606    26133718 M   resume_workexperience resume_workexperience_user_id_fbba1b93_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.resume_workexperience
    ADD CONSTRAINT resume_workexperience_user_id_fbba1b93_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.resume_workexperience DROP CONSTRAINT resume_workexperience_user_id_fbba1b93_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    272    4520    230            9           2606    26134205 W   social_auth_usersocialauth social_auth_usersocialauth_user_id_17d28448_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_auth_usersocialauth
    ADD CONSTRAINT social_auth_usersocialauth_user_id_17d28448_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.social_auth_usersocialauth DROP CONSTRAINT social_auth_usersocialauth_user_id_17d28448_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    321    4520    230            B           2606    26134394 J   social_features_comment social_features_comm_post_id_02df961f_fk_social_fe    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_comment
    ADD CONSTRAINT social_features_comm_post_id_02df961f_fk_social_fe FOREIGN KEY (post_id) REFERENCES public.social_features_post(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.social_features_comment DROP CONSTRAINT social_features_comm_post_id_02df961f_fk_social_fe;
       public          u2m65eq7rc7j8s    false    4738    324    333            C           2606    26134399 Q   social_features_comment social_features_comment_user_id_675fed60_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_comment
    ADD CONSTRAINT social_features_comment_user_id_675fed60_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.social_features_comment DROP CONSTRAINT social_features_comment_user_id_675fed60_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    333    4520            @           2606    26134382 S   social_features_follow social_features_follow_followed_id_bdbc53f2_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_follow
    ADD CONSTRAINT social_features_follow_followed_id_bdbc53f2_fk_users_user_id FOREIGN KEY (followed_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.social_features_follow DROP CONSTRAINT social_features_follow_followed_id_bdbc53f2_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    230    331            A           2606    26134387 S   social_features_follow social_features_follow_follower_id_dc6192e1_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_follow
    ADD CONSTRAINT social_features_follow_follower_id_dc6192e1_fk_users_user_id FOREIGN KEY (follower_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.social_features_follow DROP CONSTRAINT social_features_follow_follower_id_dc6192e1_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    230    331            >           2606    26134370 G   social_features_like social_features_like_post_id_f8c78122_fk_social_fe    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_like
    ADD CONSTRAINT social_features_like_post_id_f8c78122_fk_social_fe FOREIGN KEY (post_id) REFERENCES public.social_features_post(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.social_features_like DROP CONSTRAINT social_features_like_post_id_f8c78122_fk_social_fe;
       public          u2m65eq7rc7j8s    false    324    329    4738            ?           2606    26134375 K   social_features_like social_features_like_user_id_54e40bc3_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_like
    ADD CONSTRAINT social_features_like_user_id_54e40bc3_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.social_features_like DROP CONSTRAINT social_features_like_user_id_54e40bc3_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    329    4520            ;           2606    26134316 V   social_features_message social_features_message_recipient_id_f3681f33_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_message
    ADD CONSTRAINT social_features_message_recipient_id_f3681f33_fk_users_user_id FOREIGN KEY (recipient_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.social_features_message DROP CONSTRAINT social_features_message_recipient_id_f3681f33_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    325    230    4520            <           2606    26134321 S   social_features_message social_features_message_sender_id_5d2bb113_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_message
    ADD CONSTRAINT social_features_message_sender_id_5d2bb113_fk_users_user_id FOREIGN KEY (sender_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.social_features_message DROP CONSTRAINT social_features_message_sender_id_5d2bb113_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    4520    325            :           2606    26134329 M   social_features_post social_features_post_author_id_b04d5c3c_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_post
    ADD CONSTRAINT social_features_post_author_id_b04d5c3c_fk_users_user_id FOREIGN KEY (author_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.social_features_post DROP CONSTRAINT social_features_post_author_id_b04d5c3c_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    230    324            =           2606    26134365 Y   social_features_userprofile social_features_userprofile_user_id_ede8536a_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.social_features_userprofile
    ADD CONSTRAINT social_features_userprofile_user_id_ede8536a_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.social_features_userprofile DROP CONSTRAINT social_features_userprofile_user_id_ede8536a_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    327    230    4520            G           2606    26134458 O   socialaccount_socialtoken socialaccount_social_account_id_951f210e_fk_socialacc    FK CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_social_account_id_951f210e_fk_socialacc FOREIGN KEY (account_id) REFERENCES public.socialaccount_socialaccount(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.socialaccount_socialtoken DROP CONSTRAINT socialaccount_social_account_id_951f210e_fk_socialacc;
       public          u2m65eq7rc7j8s    false    4760    335    341            H           2606    26134476 K   socialaccount_socialtoken socialaccount_social_app_id_636a42d7_fk_socialacc    FK CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_social_app_id_636a42d7_fk_socialacc FOREIGN KEY (app_id) REFERENCES public.socialaccount_socialapp(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.socialaccount_socialtoken DROP CONSTRAINT socialaccount_social_app_id_636a42d7_fk_socialacc;
       public          u2m65eq7rc7j8s    false    4765    341    337            E           2606    26134451 P   socialaccount_socialapp_sites socialaccount_social_site_id_2579dee5_fk_django_si    FK CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_social_site_id_2579dee5_fk_django_si FOREIGN KEY (site_id) REFERENCES public.django_site(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.socialaccount_socialapp_sites DROP CONSTRAINT socialaccount_social_site_id_2579dee5_fk_django_si;
       public          u2m65eq7rc7j8s    false    313    339    4708            F           2606    26134446 U   socialaccount_socialapp_sites socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc    FK CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc FOREIGN KEY (socialapp_id) REFERENCES public.socialaccount_socialapp(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.socialaccount_socialapp_sites DROP CONSTRAINT socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc;
       public          u2m65eq7rc7j8s    false    4765    337    339            D           2606    26134438 Y   socialaccount_socialaccount socialaccount_socialaccount_user_id_8146e70c_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_user_id_8146e70c_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.socialaccount_socialaccount DROP CONSTRAINT socialaccount_socialaccount_user_id_8146e70c_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    230    335    4520            �           2606    26133278 F   users_user_groups users_user_groups_group_id_9afc8d0e_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.users_user_groups
    ADD CONSTRAINT users_user_groups_group_id_9afc8d0e_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 p   ALTER TABLE ONLY public.users_user_groups DROP CONSTRAINT users_user_groups_group_id_9afc8d0e_fk_auth_group_id;
       public          u2m65eq7rc7j8s    false    226    4509    232            �           2606    26133273 E   users_user_groups users_user_groups_user_id_5f6f5a90_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.users_user_groups
    ADD CONSTRAINT users_user_groups_user_id_5f6f5a90_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.users_user_groups DROP CONSTRAINT users_user_groups_user_id_5f6f5a90_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    232    230            �           2606    26133292 T   users_user_user_permissions users_user_user_perm_permission_id_0b93982e_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.users_user_user_permissions
    ADD CONSTRAINT users_user_user_perm_permission_id_0b93982e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.users_user_user_permissions DROP CONSTRAINT users_user_user_perm_permission_id_0b93982e_fk_auth_perm;
       public          u2m65eq7rc7j8s    false    234    4504    224            �           2606    26133287 Y   users_user_user_permissions users_user_user_permissions_user_id_20aca447_fk_users_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.users_user_user_permissions
    ADD CONSTRAINT users_user_user_permissions_user_id_20aca447_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.users_user_user_permissions DROP CONSTRAINT users_user_user_permissions_user_id_20aca447_fk_users_user_id;
       public          u2m65eq7rc7j8s    false    4520    230    234            �           3466    26133084    extension_before_drop    EVENT TRIGGER     u   CREATE EVENT TRIGGER extension_before_drop ON ddl_command_start
   EXECUTE FUNCTION _heroku.extension_before_drop();
 *   DROP EVENT TRIGGER extension_before_drop;
                heroku_admin    false    352            �           3466    26133085    log_create_ext    EVENT TRIGGER     a   CREATE EVENT TRIGGER log_create_ext ON ddl_command_end
   EXECUTE FUNCTION _heroku.create_ext();
 #   DROP EVENT TRIGGER log_create_ext;
                heroku_admin    false    350            �           3466    26133086    log_drop_ext    EVENT TRIGGER     V   CREATE EVENT TRIGGER log_drop_ext ON sql_drop
   EXECUTE FUNCTION _heroku.drop_ext();
 !   DROP EVENT TRIGGER log_drop_ext;
                heroku_admin    false    351            �           3466    26133087    validate_extension    EVENT TRIGGER     m   CREATE EVENT TRIGGER validate_extension ON ddl_command_end
   EXECUTE FUNCTION _heroku.validate_extension();
 '   DROP EVENT TRIGGER validate_extension;
                heroku_admin    false    354            �   k   x�]�1� ���V���y��߫�!�l2���S�8p�ø.R���E���r��3��d�����0�|���^�Fc��wwc�E+�k�k�@�~����B�01      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   �  x�}�ۖ�6����	�ɉ��A{۵��LfJ6�=�}�ږd������H>(��o�y�}ݜ���4�ןU]����}�uMD���	(jR����t�V�I�.�?��'`�A�>Yv�����v\檉�i��Z� d�;X��e;��@F�KV�_���j�����/�8�g���M��9�4j� �
�n��e^��m֟���!�Z\�Ys2�����e<��V��h/�C��6����`�s�h�U��L��ڨ�'X�)�JH�שڒ9��5��+�D "�1!&⹛~<vj��o��pܯ��!`Z\��,�8�;�l�&����31�:U#������؛�+ 5FUR4��a�9|B�F��̇��ş�׮� �~�qF ��gĄ� � ��Ƚߦ�&��i���W>�5���C�k!����\��H�vg���#Ut&�h�_���7W5-|�:H�<+��d�Τ��h~�����&������n3�����3׍8R�?���4ʧ��x
WW?[T5M��\q_�lJ 
	��� Z�x�y����L�]w��p}W��+�C(�K�r�u��ܿ\�N�Ь'��r�ת�u�b�]��K���E��"��A��+O!�E u���r:x�֛��m�G���	���'(Bo��+=A��&�'�l��c�����v��#U�_,�{�b����3Uj�d��)^�2 �*�7�aA�&eqn��$��vR�$�rf6��oa�SX�jZA���������|ZL5�Mp`�XCjF���~���VW�s��"l�P��J�eL�&I��	a���x���~��lih�����F��B!��"��B$�"����"=zR5�:��max ��n
;c�s㘙�ƍ���n^�Cմ���{)_���#\��Z`x�n�W.�y�Ԭ�\�6jZ@C�	����� ��؅\f�(:�K4�lX7��m��>}[hr;H��6g�$�|���(����^Χc�Қ�qk{�.oǓwu�v���YH�7;EU@�
�sT�I��O;I�5�N����w�
(�����[�L��T\5	iA��(���UtL�48
�b���1�3�F�d�li�ok"��~��ᎃ;�z$+�$*��Y$�)���G�8����żn����>ZZ�R;5{$�#��%d�#��r�-�<�QI�Pչwq+��ֱ���������� �`AW� ���a���oUKk���]���� Y� [D��=�P�f���ji	����Z
��/ �� �2&q�;�2uj���?&��ִ��â
��+PrX�(k�H�%(gNvq��>��E��q�F��Ѯ�ح�Q�ٮP�͍�l����v�(j���Cٯ[�n�۩�k�|��ef�Be��]��Lb��p2�uiVC�f��4OW�������r�'Z�?u��e�gO�:�W��|� ��� ���C5���{224�ñ���*��'}1>�a����b��Úg�d�p�̃tV�~?�6�e�MUK+xh�6O��Tx2�R��]�4f�*ѣ�7��-|b8O�Zu/R��������p��'�V�����:3-���:Z���0)�V&��غ��	F�hUBz	?]�A ��"˥w��߻��'t��[A~�	�S�ɏ��`O~P���J�9�F�8�fN��ά��jD̚�߹�?�ay�P��5��0��Vۢ����Zm�9���-��;\�N��/�@�""b�8����?{���%�o=1n(�u%�܀��J��s��.,A��#"��<Վ�w�?:Վ�w�xt���"�/O���s:~x�V�p�j��H��d	��DN�����N�ԭQ���N�g��bAw��W��HD�blK�L�+�I�����ۿ���&ܼ��(��1��T���6XJI����;���t�ѱ������<�m=�����d{N�h�J`��)Y\��[����imm�YSr\ dK��Aa�%��|�5[�e=�ɱ�o�K���,9��l��)��/� 1ٕ�˷��PIt����<w��-S�$*���FKS���I��@[��{c����o��W�wr`�Uɴ63<�ڌpZ���Q^�	�c���]����5�������1"�FHkF�.��ܿ�����n�o��������V,{j��oH���8����      `      x������ � �      \      x������ � �      ^      x������ � �      b      x������ � �         �   x�u�K�0���W�n(�M8�8�E/$M����%<L��-D=i2{ؙ�7����0�����R�FT���xvգ��*�k'��j= �@�i�����`O�� Utk��`���Vt���2����OX���6TP�YNl5ɽ_�ߏ̻�D.�ܐ��a��>	�,	���(^���)��8/�N$      �   �  x���OO�@��ΧX�ڲڝٿ>�*EP��J��r��[��q\۴�߽�v %�(T����~����'�@1s�5L�M9��|�X�ɢq�EQ�e�����+J��W�C�!�3(+�� P�E�]Sr��!PE�Em<|+��W�-�l��=��P�J�U_UMW���n�-]u��yJ��?
_�mx������Ys[t���%�Sג��]��_��_~�^q	)3Ԁ���H.�ʭ|N>�G�j�4��T*,�7Qɓ>i��6��=_���բߓ�i;����=���.9���P?�*�o�5e�Ԃ�\�'��_)��eʐJ��>lTJ?FNx�L��`A�
y����99v�#Y᫮h��Z/H��\W�+�m�>�/��m��Uз��,��$Y\��u�!`��l]�#�	@* �J�L��k��D^T�y(�F�'��� &�z�=���(EY���� a,e"EA�Tb����,�ex
��<B����xN�b��{y��*��> ��� ���[�",�K�9�{��$��
C���������M���#B���d����'�jT)��m�J=����;4�4��p�5U���[�R�Q�R�J�P�D	�-�����fTR��[,]�1��ʑ-3|�b��Î�*R�=�k���H�àe�V����?�dL�!�9������Q�V��k��#� ����f��ª��      �     x�}�ݒ� �����}��Jm8���o�aF������9���L��L�	��șX��-hg�4��L֬��7ړ�?t� *�0�p�j�'[xBÜ�P��C��0�b샱}�z3 t/P�#����F�:��}�S<߬�	����f՞�,��`i���#�����2y��;Y��gyY�7?J�\��m�^gd8��3U���P3$���Y��r���J�h,N&t1?pȋ�������ݍ��TI���z4�׉��-֌R��ITQ�W1j��o��t�"�#���؇93�����T�ݩ5��X�"��~P�s�oP��ӉO�Tmq��mE��#9z��h��g#� ������]�0aZI�?�w�no���/`���Pf�#�����%?Jf����e)����h����+�Y=�(�Jn�G����4$��lޤ}���MV�J�{�Q�ܡ���C�}şiC��}���z]�{�"|Z^U�_����P�Cu�z�%����ųx��*��[���{�K��&;B����߿ �2��      �   �  x��Zݒ���v�"��>J��7�r�(�f����d�ӟ���l���&�ewZB�����m{��0|��~��esj��:l�f�����|��`B�O���1�eW�_u9����)Oձ^�⅕VY�hS]���C�(�#�!��0�]y��c��M{
#���Oy�O{���N+#��R�P���Ǫ9<GqwR	�Q�"s�O�N{�9�b	�y3A��P�Cyh�^�rXX���(슝@4v�����T�%[���L�wq�'�:4�jh���v��+�u�W�z�d!�u2�q6��ťy��JZ��&�OHn�B�C��9%�+r��8��]{9c�1^��B� 31���r���k�|dt��0D�������\�o��t����0�(����>�cĸ��m��n��i�$�S!��<$ 7y��4].�q�l�/��`�Un��/������寺kޛz�f]\(Nqw]�.��w]{N؏ m!�s<pO�R݂5�?��sc��:�N�ƻcs�d�R�Y%���#� ������O�s��?�xTl����gt��r��}���6�yZLz�&���}_������qk���*��Y�xJ��E��U�x�N�H� �-��G=K�:7N��Q���#��B�-�$�fwy��^�\���A'�;H���Ӯ<�ݬV�P��@�	���j����az�?Z����DGL�c��'���qe� (]
�¶���K��%��d�h�<��'<�TH8�#��d�pO�7�!��� ��-�O0͛�w�va��WBm�1�����ܾ�oM7�C�����d8j�ѝ	�%���'0/���`���i�5�l�X�QW��h`S��uٵ�:��z�aD!�s(!Y6���w����	,��
fi$�`]Y�.�**_Sv~}���X@�e�
PPc)�(��_y=��e(��ٿ�[94��Y� ��Dw���E��9�)X�'ܺ��&�l�Q������`��vYAfyɸ�]60����,���#͏̒��K"�!RV��ϒ�?K�9����*Kn�� $w.�'Y&p���������ܭ��RDFe�lL���$R�Ab<U|z,F<pL��D�QW��^�@$��٢�da�N����|h�������S���z�d�$��L ԋì��0]���6����e�w�B�Po���K ��l+��;��kn��v�e�½��+b�YB���^-�]���~��@���,<�{��t�$���65s+�,xI\��։�P޿s��؎��٩�[�ҫ%$%�Y�3���o�O���H�Pg�����G?�*�\�Kl���ج��_5&�Pmb�'���g��'-^��0�܊qSRxEΘ�������>�,,0����N���_�BE,�֤���z���b3kR���(�5B��ɤL�)
���̤D�(Jz����0)Q�XX��y�?�:l�I�!h&���-,��e��BF���v���7�m2�2��B=�O��}bD�$���
-��Bj�"�M�H?n^�n�xMک�\ϲM<lN�gUq(:��l�m�UO�ꮏ�r����6h�0��/E9,�ѧ؜ڡy��鑄�%oA�yaiӞ�ڪ۽�6�/C(�V�>�&>.��؉��1O	��/
�ĳ�y�r�E(���
䰙{������`3mf���:��N�O^�h{7gu�63�b���8�ܚh�]f��
��q�����˹�P�8���.R���Z0V�Q���˺G���{�G_��e-#�0���O�\�tz���➻��9,���ړ�'z.c=��P���j��"���-��8N��t6������h�$r)��r��q�B*)_8#?�#?�.�V!��d�u엦�Vq�"PF���+Gi�ą�qfY�]���n�D� zv�P�{r/���C������N2<�7~B�]�,��ya]���)k�
�h-׈���R��i-3��5j.���Nd��˨,W��x �;B[��XF`������vǎ�s����f�Y�F��K��|�7��;n� ]Ȍq0qJ��k�Us/�� 0;���s�����rxz���t���xZǹ���X~v3C�F#w��|D�w�����]��7��ċ9��G~	�"���L>��۽�W��A`���L��L^G>���ǭw�|d���IF%��- �BE�2����ˋ(��TD~��2!�h�
',��"���Ei�Pp�K쀇"bz��46p��|���l�3n���s�&��Gi�#ǅ�øi=֖L��U�ٱ���Z'�����{C���?�0
-I�]a�I��f�Y�},�8J=~Q`� "�~|췼��]���*O��HQ(�ۊI�9$��f�y��b-���q�.N���Ɩ,�pBc�xNƉ�Q�t�y���n�S��'�����t��7<�p��\!Z
��?�m?ċ��??���5j͏�|o���C�F��ǥ��Fri�$^�g3����&u���AٙS _��@�%%��n�`T5���RHσE9�?�S��3Ɠ�mVhHA�1s�w~�r�lg�?�w��/��9������_�.�b_��KS������M��Q|O�-U�v�hh6�w\l��h�:���	���H�܉�O@̯��D�ț���ԣ�{��<qma~#����|�6w��k))y\)�P^�m�?���8�BQxBH��X��B)x���PA��T�r���!_'5��5������5��b��и37�L��[{�<}#���mל���\g�We��a�������Q���M@��v,�Zo��'t��f������a��%���!�f+J<��rB��Ĩ���iZ`	��J��X�A_�̸��P"{��e?f�C&~|��A�������=-�k̀�o ��밯�������^�����A�ʷ�~֠a�Ia�� ~��7�I�v�oE����k9��І�
���o�e>̌������_޺z��l_Ta��qLN��������3�V��iӒ�{���/�V({�7ϭi�S�a�FRL���$½է������č���\Υ?n�����+�-|�G�5� ��i�����̟�{�eh�c��������      <   �  x�՗I��X��י�"�-���;l�0�A-Y��<�니�ʡԛ^�[[q�w�9�.�>"t?/�6�h����X�[
��_�"a�rvP���.�I��vQG�޳��*�P���[��0��;�t'��E��e�:-M����o$��]o'�+����G���۬lJ=�ȇ�n.	����j�Q�h����(�i���#�hN�hK���?	�OFJ��!2���k��e	)��跓~�Ǭs�Y�~!�'�[TYlU���N�:A�7@��_N�(�? ��7i��uX#�^�56�>�{=`U�S����F
��jqhc8�]zr����v�I�ŗq~�+�
�0oBK����ׄ��=�ؓ�퉈S�T�^!ҟh?% �Ŧ߶Od-�4�I	�՝:Q~޻y�4��6���V�9���0Z�����B��b��*�zLe����/��880nW�����/�~���ߊ���޲{���)��~���c�?�����3N�q�����ƄL���%���8�qgI�f};�4��%ڄ�}��ϛ��_����Ց�y[��	q�jix73%6���-�(w�*\��b����v?��;&��H�W��gd���p�;�/&N�S��6���{��z��.�4w���Ɓ���gH}A�c�ϫ�Y e����@��r��9Ed;���_�B^U���A��
+�LVڵ�l4����n��R��8�>(�{#��©�ƛ(��b͔3�H�Km�C���%��q�f�UI� vX��	����R;6G�N���.����J� ���z#E�g[������õ���'���`��B�[��+�@�<o"�m= �
,E��sB퇹�����ϙ��i�,<������V�����1�PɋL2��_H�{������F�6I����G�]�v���B�!�C���+�RmνD�S�M�I���L4
��/,:s�2�ܲ�s�s���>�J��6v�aM*O�e���Z��/�~��P?�IX4���R T,����f���Oe�%cT-�\anܤ�eŉ���^	�]k�̢<��������Q����R����l5��H9�*Y�1�xfSѣ�}�6�����Ϸ�C/:�L��-iS�ͬ6Kin����F������:�4��W�e���J�^r=�(2b�4i�~$�Y�w)�-&q���ć�M���\���#������a��� $��`��ad�)��+ZGA�Ƌ�<A���AI~y*= 7��c��0�2,��-�=�ZDT�&����*�94��X��iy}��	!
�*KI�g�UMsZkB�擼mm��Kȫ�'<�n:��%� l�h����v.�5���v�*6��^$=r�G����%�&�g;R��{/��
���X%+����?w�MW[Ӕ��0���XZ���m�q��Cb(���Q_vl3�͎��`�S1��~(`4X{[4�~��#c;�����5q�/��l��7��o;Q<���i/��`\��d���=���ĩ�4*���{,
�d��aB�)Y�,��dsl�=����0���p󊜕.!A���畃{/��^����2�O��bm;�&[u�+]�o�w�Ͳɹ�M������'��j�9�uu7��)�~z��!���n�ê�[���3�ƅ��Cu��h-E��뒦�N¬�#�,��%G��$?s/���$G6���Ŏ���@C�n�M`v�b�g�����3�|��H*<J�>�d��	Ө��%D{:�S���QHag���{:�=�W7�������������ߦ����ç ����g�B�Q?�M��DHE5�!��ySKॿ+)���HH�����W��,Б N��V&�?��Y���(Nh�;�De�K���?��y\^)��Z����ըwC�5PRd4����k�t��3O��7綂����
��#�o�^9^��Y>�!g[M�o,������S�=�!Cb�W�2�[�O�M݀ \͒�m�i3�"I@W:�]l)D¤�[J:��̖��8im�L��k��c0P�GبpҜN,�F`8��k�;:�?��"(�w&L�Z��e�:u�,xM�G�����v�G�1�f�l2����t��*�`]��q��d��8�\�l��YL�r� qƨ/��D`ߌ�eM��;&�u�k<���ƨ$�&�;�Ϧ8N�#�miSg��p[�3��j�7���˳�l�1��ÿuD��|j/X|�D��{U7TF�Zc��{o������p�W��#µZ�^Q��	{#[65Ay�`��Z����1��ء#�G!A��Ԁ���	;�X�'@P�C�H?\֖�3��nُ��A{H���J�w4�c��ߨ�ӝp
��q�J�����q���u2��"��sp�E���[�ߎ�8P��Y����Cs��[f��co��2;�n�O�{s�&�=�	���Hoqmo�bi}����Dؔ~MH|���2��C7��N�BC�R-�_�4.�%�L����|{gBI�P�Zeo�'�oz�Z�'�B�#>�����Z.�u6�x�w�����ſ
~���Z�$��|SV�a�8`���k��l��o�q=�3�H`�b7�&�,�p�zC�����F� A'��h�b��G��,uԒ�ƓZ$F(�֊�(�?��,m�M1i����r��&h@�u������.w�f6.�xJ�(x����D�a6��Ox�� eV�GxxSޯ���O��S\yB��^U�\��-�����I��~���"���5�ekOx�]a��P���!���-rQ�ψS�󱘯N�ml{͢l�/�N���Fq���P�3�_E��#C�<�2���p@�d(+d�$֕���3d��?E9@�o�_��m� <��Z�ci6_��Q��-^�z}��I��X'(
��ܖr"O�}�̔*4�-�J8�xՄ:xa5~:��P�q�C��]��c�l�u_���\����K+[���x��ail�X�"�9��E{�e5
�>���-^d��5L��w����9��%7�獓�Z�/�k	+�o����'���9�"DN�)~¸Qp��E_p�m�V�vJ�y9Dp�����,�@l���g��9���=�ff�����L�c#o5�$>�����G�:�����
���|d9��Kg,*��P05m�0�H�.�8<�o:��4����u�^��! �q�J�MI�C��d���4?�� �?�����_��       >      x�3�L�H�-�I�K��Efs��qqq �[	�            x������ � �            x������ � �      )      x������ � �         �  x��Y�r�}��Oɪ��H�(Y|��뮵�ZJ\[q���5pe�S~#��/���B����Ut9���t�����`�lQ�A�H#��^�J�B�5��f0>ƿ�`1���Ň�r����g�I	��J�k�R��rUn���e�
!M!*�F|ۻI+�Xm���(�FV:A�*w+%t�d)r�l8R̕pʯ��z^*��NX���m�ڨҮ�C���e��.��uË���ȭ��:�0��M�����ʷ?Xw/��ztX��Y�G���K����&/�dRf��R�C��U�G/K��$b^�`ak���ں0$a��5LK*�:ϕ����v���[҅l=�����N���ATJ�t����{
��b^{�X:�V��>?�����V�P�<;�1�mp��r;/�G��$)�b�=L�򨣳���:��^�zi�+ю�ZK�K+K����
,<Ky��J�|5���i�K/�Qq"LH<���z�ɮ��	z����j|#���c,��6l�6��P0��e:��,�ܺZ(׃@���P>B�DJ�M����5J�+�D��Z��q$�l|��u>(�B�ۼT}$R@vM/F�5�#"���m��je��ܴA4��x��i�#��n���{��K	EV�\��C(����S����^X�z��*�庹�ŅSq�ҳ�6V�b��4���1� �ڐ�h�}�/70(���J	$�?�R_�p���2�&jE[��u���2,�U��*�0�̾�6%�9E �R��)���u)͎7�� /CvL8��6��Ȏ9�fi�qqc~�p\:J�H�*��ɢd\-�R�Y��ĠU��<n���ېd'� O��H?0Y�0�)���g��Q<_��3%d�*��B�KeG��;9ΐ*sN?7'���}�o�����f]޵�?E6�[Q�G���6�!4,���d8�-��*_[ڥn�=WdC��E� '�QY`�U��i�d��Z�d��4G^,�F����L�a��3c2�]I��RZ�����i�/Y]�H�aH�ޕ�k\T#��m��
�B�}\�Z����/6dѢ=� /u4�6>���{�E���]ܐ��]����-��gc�y�ݺe�UM��:h)B~ {��k#��t�=@^�!�yK,&����mm�8	�A�.^;ց��ڔ�+V�H�O��
�Ȅ 9-������E���0���¬��e��B�%d4٥�b�,A�|%ݒ�]�e���bp28����gy��00���`PYg���J/��n��k*������NO��x:9�O�������{�Ľ����yvyzy<����������)���7u5��9&Q̫��#��-մ!'��f�dA"��Ӟ����9PL���"�b�Aͅ\��&x�b�;�Ŷg�}^�<�N�����c�a��9%S��粤�̷�^���1eU{z����a����ЩB[/v7}�A��d�Z�v�"�Gs��}3�/Q�QK%q�Z ?in:��1B�"� |�nn��|�W�{��<�J��hO/��!�Ȗu+�;�h��� 5���Z:�
�'��:�6����_5�i���D�r�Ҟ;gk����Жܒ�s+�����/�1�[ �,�/*��Rى���#d��z-e1�;=�4J'q}�UD�f�x�ڮ�R:^��:E0DaV�2���Ixa(n��-�B�������0��$���w7���6��������@+���a���������қ���8ff}@����!��"�g8�m���vS2U#rL��9���N���K���Ej��D&o� DJH�f�;���TO^X<ΐ�z��W	�.���_���'����O�!������w,����MA�������%�c(�Q�K>F���@�n���q4�m2 ����ߣ���������f��5��6�[`�&M4�(u���U�l4��mᶪu�eN������$��������B����6%�d�(���"�b��E�O̴S��������xz�<��/&g']�o������"��]N.��N7�}Ľ߃wq	jx��gĚ�T�1�bĖf|�3��'=����;:{��>���.���n�*�]6gWHOe��FK�/M���%��L�Y����\̴���.��� $��l]K���e�Ė��U�L�	�F'S���ƂF~ó�y����O~�#[�8��?�uY4��T��5'�N~ꮸ�5|��J��{I&����.5-DT[�D��Mi<��%Gyë��85���"��=q���,��8z�7CS�.���k�aI4��RۋuC��h���>c���&�6Ʀ�'��.N�%��r��4zLdHr����6��[�C_S��U
���B5n���y^���t�0>|��-%�]~�W~���V����: u���&rMMv�f����_ān��f�����c���}�D9�ۈ�o���:�B}����F =��y]5���2��%�����jM���t�C��G���F6O��#�Z��`�����Pp�s�p%f��e��aB�w�]]��e��=�_x�"�7��R��L����"��ζ���G֓�o���#9{<���J�!̭{]��a��/�k��0�}�!j�>���Y�R�Z �2�� �Ou5�E���qg��l����F����(�N���4�h���Tk�(z״��|�����="���+����:�껟�ώ�\e��'�:�ug�]P]u�?9Yt��N�zL3�	r�+h��A5�_��c��1�Q�o(Hʅ��`*��s��W�a�2{�D�R
�wNl�2�5T�.�?{�Bcͨ����3�Q7���i��h���j���>����`WH �4U�+�:3'S(�f�r��9�x�:�[ϓ_p��1?9��=�N��������G������2?�8?;#��9{���� �&�      %   /   x�340�43�426�240�0̀L3ӂ��Є�܄��̄+F��� ���      '   ,   x�3��43�426�2���̸� ,.sCNsN#3�=... ���            x������ � �      !      x������ � �      #   #  x��W[o�6~f~�bi��q�n�c;��$�o�-�6Q�TI*�:��;���"o��s��u�>,U��f��R�I�Rz���I��ܯ��\9�;��O2��[X��.��S�;}V^��QX��I�;o�T+�K�[���[�*ii`�?g�zv��OwG�
�\
��w���y�!�<I���K��ޑuBs����wR$d��ݒO�IؽP��^�b�>��q!ck2�*���
�>i��V�����7Qq���_���{^{���;/�L���|�gH�<��|nM�EτUo�S6�k�0N��77�q|3�x��sy���G@��.��L���>�<N'wĆ|(��\ڢ�&N�g��"I�5+G�$0y�Y��1�,γDE0Ýn�3�҅X9�Ӟ�b5��F���I$�\�t2�0>2I��kQ��O�,bI��U1$�9T^2\$�J�'$��\$u ll�����\��醋*�^��m2���*	�����t��wu\�:Ծs6U��j�\�P�e�%�����'~������e���d��a�
�����ݨayπK6����K�O���b����jwY`O�`I�=�P�`SD�d7p*�z��
��Bi���Y��͚������D_	@db�[34K��N�<G�(�)}tڦx(��D�EJн��\J��6�<C"~����a��r* 륏���O�h��.��,��,���b��O����[CK�'�g����;�~�c!�E�VHx[��p($l �Sjb�-�!����޺�U;�s�:W�̦�V���fT�
����4��Q^=�4t(o�OČ���^9Vd(R�f�O��*K
2*�H�>�*��������7Aa7(LoW
��=��#�fI�Z����K�\&#0q�H�6��̸S�a �]&"��q
����>�s�ά��&�d74���J�$�0��$4�>CLJ�E򅮵�K_����n������V����m�j	�+�'q��f)x�9��Kk\I�{Ͻ>�{'����h���p}cA��g��ت�������q���JJ��YlŪ3Z��t�¬)Z.��e��/�N[+3t/�_�qiY����S����\���ݠ	�UfS�@�)F:��u�,���	�SE�SMZ���ɰR��7j�C����]Ƨ^}q�Y�J����bvR�㵆�K]
-�4r�$ǮM�;��L���7쓒+�Z��Y�"�wU��t���!  p�~J���pȑ �� ��%���ൈ�HSjo�g�B�pU��Ѽ9�f�����U���63 ?�9�/��=���!��ѡ�MM�H*j�eBǡHeҫ�*�f)���hnm�qޤx5i)c�4<�P4�p,A~J���<)1S��EY��\�!�T��
[6@bWV����tQw����d����ު��;�O�{����9�I��N	�2 �,=co#����[�A`yK"vK)��#X��9���U=a��$	��������|��c����Q{C��Ρ��1F���b��d�̧ӣ���u�      -      x������ � �      +      x������ � �      /      x������ � �      1      x������ � �      3      x������ � �      5      x������ � �         �   x�m˽
�0����UdJOl����S�`%�i�woEpr{��Q8�,;�⒢��`'��1O�};�|qO�&��R
�Hh���E^f�׼.����-�܎Ծ��6�i`ʯ%\S����lxx�K@8��+�o�43           x���As�0��ү����P��д�N�NIg:mzP��V#K�,C��ڡ��0io��~��߳6^Y#4�WI�>Z��(S�d>�D�+�;����Ă�LQ[W�]�DD�L'�SZ�`�v�ˮ',`#�-
O��2�a�,��0T���M���ZM��J�(^
#1�K\���t�P5�L��|�R������+u���5��M]��p�?B�{��H��T����&Є	�`�
�������$�r3���[��Qz�$���w��X�MsӉ���bF�e��M�? ,;u��� �v�e<h���>>�ȩ_�f^x���!�����Z��Mo�'�5}����P���ͷ�X��n ��hB�B:�;Y�Ur�;��*����<�'
�[��w΢�/0�s�ԏ�������-��ݯ��N^F�ק�Jgs*$X��Q�e8��F么)��%W��d�M� L���T-v���Q�M��؄��Q�Iqn���)��k�����+������s��H��            x������ � �      9   (   x�3�t�K��,��2�t+J�K��2�.H�	��qqq �#	n         '  x���Mk�0��ɯ�}D�d���`=�P(a3!��Ѳ�?��H�S˰O~��ǯ��j�4߻aꦗX1���[��z�tc�5 P��u�6�xz�f�>�6��}jPD({Bt��px��b�ÆU@HA*$�ng��@ăqZ+Nj�
�۩��������r̳ŏ�nHgL�`���Θ�j�1�s>��.(�^�r8S�	3\*��p��e:��)�EHhc��<�ՠ�fHB�(�r���!_NI�gH��,*�~�Z�qm��|�ٓO�Ţ m�8#b��o�:��vP�����L         �   x�%�˱e!�G�L!�6���?��+w�i�Ǐ���t<(ǋ�E.�2$���� �br���kȯB	�P$CCƁ,���d����)�3o��
�͚+��H�UH�5�=�z惴Yis.��I��(�S(�3Q6g�l�F�EM���7|�瓷˾��e:C4ݡ��l�[>+�cK��K�ƾ�ϐ�y�����\o:��,�J>N����? �ofJ-         	  x��X�r�][_��\!陑(��&E��qEY�M���@C\a��)ޕ�_H6�f��7��T����!���H��6+U�$t7N�>ݣ�WU]�����c��4N��Uf���}�mpV����ĉw6(��c5Sƕʏ�A;��h?I�V�:�^�U6�Oy!�I]1�G��9�}|��Y���:�35���,�G���E�%�転���p�k�����:S64D�Z�V�ˠ��F����b�tfT:�:�V��ﬞ)_鰠�U8-����`EY��&�H]���D!z%��V�6̥W"[_]8����fUZ{2-Ţ
+��Nߠ2�rc?�I��Fq	�*�}}-ȡ�S�w�͍�3�Ѥp��wU��P��v��)_��M����6X����x��X������$J�&~u��U�bHw�=!}"˧�q$�#���ʉ�S���j)�(~I�ⱽ��/��.6�����xə7�~s��$ȫw����������u�v�pwq�<w��;q))O�TW��8u횙C]��ir>��628ЦW��@�+Up�̟A�z�6K�r����+��܊[r.V����W#�ET�7��Ĩ�Y93HUT���W�gC�h�ר���YC��3Y�^�����d��|зZeM��>x	�yM�#��4�`��;�~E�\T�}���es%p�b7�u ;���쭩��y�Ҵߌ�q[��n|�MZ��v��(z����=��fwﰕ��vw:zs)}�Me�x����<������m��1������̈́h��cGmq�z8������w38��u�(��tK�4!C�^�y�^jR�E�T�W��;���/^�:L�	m�(�$�D{_�Y�k�CB�����A�TQ����yl�$��WTI���i�;|�H��drq,lB4TQ��=�7*��ˬ^=u�RU@eP		B��CN.�#8Wsq�k[�uz��o6���l�p&q�+����d�ޤ���?*.�{�P	���u��#T�WƇ�-yx|���3	A.p��P�+����B���w�#�;B��p9���"��F8�|���H��(6ę�h�w6�O]�Ʃ��- B��^���Ά�������S�(�>n�h��ȪY�	��,��.��j��re"+��Xxc]1��~�=�L��˜q��E�������@z&W�R8ѐ�6��Se��D��mo�JT9:����k��:�7Co�G�cL:�˓$J�d�63q�_�A�v�61�[�D�J�i�+�~0���|jmkI�m!�
k� ,�2��0�ٵ����r�� ��OC�������V��HDZ�����w5gW$�0��_0Y��bķ�����hn���	��T�byC�CG�'5�Y���"U��w:��I;DZO�.[����S��z]�TlHy�	)�e���"��/������75��LFߞ���:�׌V%�;��!� �xU���ҝMC�IN1m�/�������쉑���s:���q�+�x�Y&
�똭�u�E!q�m��2���ȢY���/�?)j��Em�R���Cs��)�Z�W�]������B�����B���[�hzc�\���b�	���q�&���
�P���l���$��3Ԡ�A�nN3�!�,0��l)��䯏 ���:�b���P�rz�h����D�I9#�����%��%Q$�1@ ���8��~���:���#Π_�Õ��\j�3�.dũ�j��3�eFm�-)�h+v�i/4��֯���d���Ү��xS��ԌБ*�vb\��%�4�^Mfi�����o
�Wb
�bk{�j>l~9��}�
\	8Y���'�Nğ�_���֗�I5�n���o��PmUt&�	�X�;$\����qh���nq����f�$�DA�8p�2�+q�^%kJ/b��&O1���3�SY���bG=���{3g���].ÿ́�6B�Șb��=ޥ��WȻ�2�5��/��RnԌ����s��ߒz7Bl�A@&�AV%�A��z�`��`N�<v��C]ﵘ�tH����V�o#�����9������ՠtaM��Ŝ"�K���B)zh=f�TZ������s9��Z���v)�pL����޲x���9�C�e���_6�X${�{I+����|߉~�@g/ټ `7Qԍ�n����(�ݝ�������4�?��Os����4�?��Os����4�?���﹟�su���n��?�<��?܏��I�}��V��%�ְ3n������+=         1   x���  �77�(��ρ�_��l��H������q*��xF�         O	  x�uX�r�]���U���)wDZ�%-ɏi٭Uݙ�l`��&	$��,�k�HU*����9�$���p/��9p��ޟ����y�U��F[o��B�ʏ�JO��]_c�;�YЇ ^G����h+@��{U��+h�ɤ�E!�2��F�ieꤪ����١T�Ս�]$FVҟ�Rm+��o��N�A��Cjt��͋�2��ťk��6�(w�T�R���C�Ƶ��C+"�冷d�R��G<�;��}�F�v��L�_�ye�r�1Z/�^���S�[�	!_oU��yf�y��<_�H���P�\%NN��f�J[���|��MyE����Z=%��7�2�)��,K�6P�Q �F�,�/�8{��pl����0 �ͯ��L�\p��2ީD��{��J�*g�I����:�m����[#��o�$�����]�7i��PV2w�!Wd�";W��3�UTc1\���2J���.����~���!����LS���l�b��ބ���߿������P�h�u�:��/���qbԎ��Oş��ĝk�>�{�~t*2ws�z��Q��d<�T~��6l.�*�(2ؒRG*W'2q��WixM&~���)��nY:�t�"����oC��q�WgȈ��׆�b0��;����OXf��h�e2��{��KoH�E�N��oM���(It]��C�@Q$�;����J���Y7��G��wl�|]��v��dhK9U��(1���D�G!%�N��(�,Ϳ'��~D�|�U�z��,#�%��� '>� X�/n�����\}D����Y?�8��h؈��������hԶ��K�6ϙ5ȏ�Lkt���k�1\�N����J�ҟ�Ww�8��5��j����ˇb/���NRƶg0�7��B۷� EY�Å�֩�iw|��v��W�U���b��D)�I^Xa�����(���w��t�@�]�Lzg�YI��&3
�]�2=�1�]qAO�����̤�0�D�W����Y6�2����U.^[���"E2^Ԏe��Z��h��_�:�ةR��Š�f����c^�dnUBM\-`��đ[�����G>�"s�	z���c;<������gc6��f����*{SE�c��fy��Ao�'` :`gpe�!7/�ފ���,y�H>�n5�����������[��=��+�ߨ��Z���^�G����I�v�t�`H����N<���9C��z�-�h=��[�����O3d�G&�'ޓ��?�ҿ�LBl�[�v ҏw�	�S��T�m����L���#�6��E�iW��z(��kY��l2�Ɨ l\��`�'��C ��(��-'�-�l�|pD�ڃ�5XL����Ȟ�`�JT�Α����WWU��N�*`���w�����h�]��h��`Rjr��QT'����ɆI��0BL�3E�E�~�Ǯ`_ na4D���~����������U��]rG��Na�q[Cn6�ɞĿ���vj#���HE�����|�J�,NT�B/�j��*S�N4����B���&����M�A�>J�ނ�f�t�µ�ұ�[�9Q��8&i�� �X�j
�BP��=@���̬쌂Z@�N���:��
�d��g	Qi~�[�v�� A��R��.� �+t�FW��<kl�ӗ���$ow@�90
�߶,�߀I7���
�ӹ�#eu�r�0�>�=M����{��L���l�gQ^�B0v��F��	��g�М���9���<u-J�z^�p�Rҙ��L���B���<^ojи�C������j��~ �O�"Wi�xk��;2��f�J��� >F;pB`?�l8��?;$M��c��Ė�b#�$�Ê��0$�>25V�^�[P�٧��70�����Ic�k�XV�Y<X;8���"�O�5X7=� p�.a40��;�>Q�$��pL���s! ��ut}��ac0""���#� �����(��ϊ�<vc�]����w�/ߦ��@eн���*[k���P<け��F��Ku��C�#W�q��߁������J)�)�'cG�����F�uRa�yC�a�X[b����ݰ
�Y�C��ɝ�v^;���
�75�慿5��z�Kfx��<tk�YB�i.v~r
�a��:�P���5���F��fv�BIЛY�#���Fb
��x���7`����G4�JNF��$���+^���%�r�!^�aR�o���;��|�7�8\h@bPr4Vɻ�vlɦ�Z�L��C xnW
:��e�=0���-'D%����\
"�= ��N��=��I��3=?�ِ`�kLU�/x�;M�]��VG<�0�>�JD��-q$��D�5 OL��E<�;_jّ��ûw�����         �  x�-�[�$9�U�Y���]���X�� �)��eZ�1��1�]��ݱ�=q��q�}���(}���R�����BJ ��*)tR2(���J��6$��� C�zf�Ɗ���1�'z��@oT���75��b�7wL���ޘ���Y1�[_L�V�Do���-	zK���:��[7z���U,�������#z{�BoK���Eo������b��+6z��:dl�Έ�ޙ��;�A���O���O4V�'�w�8�1C?�8����q��hܡ)Oh�F����w�����دƌ�q�E�͸�׿�q��C�I��K���x����x�Ո�^�x�Պ�^�x�Չ�^�x�ՋB�t-��������3jV�1�k8Q�p�ʠ��>����W����&���.���6���7�S���\p�;���	�t���#�r�$IpZ�,8/IF'P
�L��&Ʉs����Ir��$�pz�l8?I:��$�P��(���k�����YJ��4%Yq���8QI^��$1NU��*I������J���5�<�+I����KD E�G$E�G(E�G,E<Fi�<�)���u\7�n�sݠr�D�u��u���M�Z��]7�n�uݠ�A庉��A�A�u���-�����=�t]7�nP�n��\7(]7h�n�<�=j�n�vݠ�Aו��+�k����%$��L(�I����BIk�Fik�F�k��g%#�cɤvn�&�u���w�̴yc�҈[5ʭzĭ�~ �j7W�7�6&r��Ne���e�������!E�ňQ�ʸ��kXGr��z�jo[��-�j��#7f8��@�Wi	ZǹB�qs6�I��0�Q��0�Y�� �ʴQ�.�Q/�n�QO���Qo��n��n���nt��n45�S��r;�QnZ�Qn4=Pn�=Pn�>Pnt?Pn4@Pn�@Pn�A�\ �nrۘ�rۘ�rۘ�rۘ�rۘ�rۘ������ژ��l�����?Wi�      	   n   x�]˱
�0���)�BkMq�ҥp�rğp g�i��ή|zXV�Z�+=���F�fC�~���U�� Mܜ�to�{:��S���Mͽ�$ݏ_���n�O���%�      ;      x������ � �      7       x�3��4�2�t�4�23��47������ (�/         �   x����
�0���Sd�E��g[�Eu����E�֧7��n�;����ai��Ze�ׄNvP�W���"D3h��b�7�]cd��8E�o(�#>����(�#��N�WÓ����}Ȏ����k�,��OQ����m�'X]��� ��ۤ�&��3�4��כ	c�ON�      @      x������ � �      B      x������ � �      D      x������ � �      H      x������ � �      F   _  x�M�Ao�@��~
�u�ya��j+�.J�`6!0�2�,��~�JO�>�<��� ��Tp��/M�$B���]��i�BcU9�@`���FYYH׈n 2~!�S1X[�	����
����k��һ��Ǣ&/�m�&0)�p��*�1j�S/ʌ�g~V�c���o�j1���C��ߜ���5)�8{^=���mwƞ9�O����/��6��i������'o�"�7v�J#mW�>~]�GqX��]���ť��0�5�嬀ub;''������������w�fZ�2�΃N��c��#���y:S�����n�� 6y]�mz�i��1[�6���I���?m8~�~�      R      x������ � �      P      x������ � �      N      x������ � �      J      x������ � �      I      x������ � �      L      x������ � �      T      x������ � �      V      x������ � �      X      x������ � �      Z      x������ � �      �   -  x���Yo�H���ȃ�Z�k����N��v�M��F�Ƙ%�ӿ~����4�P]�)��O)6|�A��;Q�d������ҁ̆�}�k9�Ǵi�w6�l��/6y��~;�fl79���>�����YW�&!��#��<@� 2�X@� ɑ�Q�F��@���J�YCT��3Lq��YV.-2�d׊��3`�@NJ�{UQVԇq\�g�!�x�kO�-`��M$^Ŗ�u>&���"��d�ucg��]K�'}�]D���<���
�
Eq0���cny�}���6�[5����R���LZ�v�?.���:!Y`1��OQE % � Nx�O�+|ӁF��u=ݏ����Z�u�����ҍ��bi8��~g�!�t��N�a���h��/V -���N��1^�E�����U�TDe�A/ĄG�Si��ݐs��X�����
�
�2^�냙��*p�j�d�ш6E_�vInX�gn��"�=e��ä��ڊ�����h�ۯ�n;���

nVĥ�dx�����ns!���D)%�WD�v��#�"���9�
d�`�� RP�pɄ�g���Y���]�e�ś�ܴ�֛Џ���yDBO������_'�����MOKq/.6Ơ��H���b[O�{��T���}�H=q���5��M�,���x������A��K"�>����~�����J���֐�M�����]�é���߶6�X��M謍|�_�w�ɦZ�a� �R�R"L�u����ޟ)��Ga��&]=�Si\�j���YrurqVN?��X�7���ƿ;���      �      x������ � �      �      x������ � �     
