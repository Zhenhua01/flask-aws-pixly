--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4
-- Dumped by pg_dump version 14.4

\echo 'Delete and recreate pixly db?'
\prompt 'Return for yes or control-C to cancel > ' foo

DROP DATABASE pixly;
CREATE DATABASE pixly;
\connect pixly

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.images (
    id integer NOT NULL,
    image_name character varying(50) NOT NULL,
    uploaded_by character varying(50) NOT NULL,
    filename character varying(50) NOT NULL,
    notes character varying,
    upload_date timestamp without time zone NOT NULL,
    s3_url_path character varying NOT NULL,
    __ts_vector__ tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, (((((image_name)::text || ' '::text) || (uploaded_by)::text) || ' '::text) || (notes)::text))) STORED
);


--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metadata (
    id integer NOT NULL,
    image_id integer NOT NULL,
    tag character varying(100) NOT NULL,
    value character varying(100) NOT NULL,
    __ts_vector__ tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, (((tag)::text || ' '::text) || (value)::text))) STORED
);


--
-- Name: metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.metadata_id_seq OWNED BY public.metadata.id;


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Name: metadata id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metadata ALTER COLUMN id SET DEFAULT nextval('public.metadata_id_seq'::regclass);


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.images (id, image_name, uploaded_by, filename, notes, upload_date, s3_url_path) FROM stdin;
\.


--
-- Data for Name: metadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.metadata (id, image_id, tag, value) FROM stdin;
\.


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.images_id_seq', 1, false);


--
-- Name: metadata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.metadata_id_seq', 1, false);


--
-- Name: images images_filename_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_filename_key UNIQUE (filename);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: metadata metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metadata
    ADD CONSTRAINT metadata_pkey PRIMARY KEY (id);


--
-- Name: ix_image___ts_vector__; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_image___ts_vector__ ON public.images USING gin (__ts_vector__);


--
-- Name: ix_metadata___ts_vector__; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metadata___ts_vector__ ON public.metadata USING gin (__ts_vector__);


--
-- Name: metadata metadata_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metadata
    ADD CONSTRAINT metadata_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id);


--
-- PostgreSQL database dump complete
--

\echo 'Delete and recreate pixly_test db?'
\prompt 'Return for yes or control-C to cancel > ' foo

DROP DATABASE pixly_test;
CREATE DATABASE pixly_test;
