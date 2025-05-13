--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Debian 16.2-1.pgdg120+2)
-- Dumped by pg_dump version 16.2

-- Started on 2024-06-10 11:24:39 UTC

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
-- TOC entry 233 (class 1259 OID 16579)
-- Name: workouts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.workouts (
    id integer NOT NULL,
    coach_id integer,
    customer_id integer,
    chat_id integer,
    name character varying,
    type_connection character varying,
    date_field date,
    time_start timestamp without time zone
);


ALTER TABLE public.workouts OWNER TO "user";

--
-- TOC entry 232 (class 1259 OID 16578)
-- Name: workouts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.workouts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workouts_id_seq OWNER TO "user";

--
-- TOC entry 3413 (class 0 OID 0)
-- Dependencies: 232
-- Name: workouts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.workouts_id_seq OWNED BY public.workouts.id;


--
-- TOC entry 3257 (class 2604 OID 16582)
-- Name: workouts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.workouts ALTER COLUMN id SET DEFAULT nextval('public.workouts_id_seq'::regclass);


--
-- TOC entry 3407 (class 0 OID 16579)
-- Dependencies: 233
-- Data for Name: workouts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.workouts (id, coach_id, customer_id, chat_id, name, type_connection, time_start) FROM stdin;
1	\N	\N	\N	Руки	ONLINE	2024-06-10 11:20:20.794
\.


--
-- TOC entry 3414 (class 0 OID 0)
-- Dependencies: 232
-- Name: workouts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.workouts_id_seq', 1, true);


--
-- TOC entry 3259 (class 2606 OID 16584)
-- Name: workouts workouts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.workouts
    ADD CONSTRAINT workouts_pkey PRIMARY KEY (id);


-- Completed on 2024-06-10 11:24:39 UTC

--
-- PostgreSQL database dump complete
--

