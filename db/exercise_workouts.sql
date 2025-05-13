--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Debian 16.2-1.pgdg120+2)
-- Dumped by pg_dump version 16.2

-- Started on 2024-06-10 11:25:38 UTC

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
-- TOC entry 235 (class 1259 OID 16601)
-- Name: exercise_workouts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.exercise_workouts (
    id integer NOT NULL,
    exercise_id integer NOT NULL,
    workout_id integer NOT NULL,
    num_order integer NOT NULL,
    num_sets integer,
    num_sets_done integer NOT NULL,
    num_reps integer,
    stage character varying NOT NULL
);


ALTER TABLE public.exercise_workouts OWNER TO "user";

--
-- TOC entry 234 (class 1259 OID 16600)
-- Name: exercise_workouts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.exercise_workouts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exercise_workouts_id_seq OWNER TO "user";

--
-- TOC entry 3412 (class 0 OID 0)
-- Dependencies: 234
-- Name: exercise_workouts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.exercise_workouts_id_seq OWNED BY public.exercise_workouts.id;


--
-- TOC entry 3257 (class 2604 OID 16604)
-- Name: exercise_workouts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exercise_workouts ALTER COLUMN id SET DEFAULT nextval('public.exercise_workouts_id_seq'::regclass);


--
-- TOC entry 3406 (class 0 OID 16601)
-- Dependencies: 235
-- Data for Name: exercise_workouts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.exercise_workouts (id, exercise_id, workout_id, num_order, num_sets, num_sets_done, num_reps, stage) FROM stdin;
1	1	1	1	5	0	10	MAIN
2	2	1	2	5	0	8	WARM_UP
3	3	1	3	4	0	5	MAIN
4	4	1	4	5	0	10	COOL_DOWN
5	5	1	5	3	0	5	MAIN
\.


--
-- TOC entry 3413 (class 0 OID 0)
-- Dependencies: 234
-- Name: exercise_workouts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.exercise_workouts_id_seq', 5, true);


--
-- TOC entry 3259 (class 2606 OID 16606)
-- Name: exercise_workouts exercise_workouts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exercise_workouts
    ADD CONSTRAINT exercise_workouts_pkey PRIMARY KEY (id);


--
-- TOC entry 3260 (class 2606 OID 16607)
-- Name: exercise_workouts exercise_workouts_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exercise_workouts
    ADD CONSTRAINT exercise_workouts_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercises(id);


-- Completed on 2024-06-10 11:25:38 UTC

--
-- PostgreSQL database dump complete
--

