# Converted with pg2mysql-1.9
# Converted on Tue, 25 Nov 2025 09:41:30 -0500
# Lightbox Technologies Inc. http://www.lightbox.ca

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone="+00:00";

CREATE TABLE public.account_user (
    id bigint NOT NULL,
    password varchar(128) NOT NULL,
    last_login timestamp,
    is_superuser bool NOT NULL,
    role varchar(20) NOT NULL,
    user_id varchar(20) NOT NULL,
    full_name varchar(222) NOT NULL,
    is_active bool NOT NULL,
    is_staff bool NOT NULL,
    gender varchar(10),
    date_of_birth date,
    nationality varchar(30)
) TYPE=MyISAM;

CREATE TABLE public.account_user_groups (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    group_id int(11) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.account_user_user_permissions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission_id int(11) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.auth_group (
    id int(11) NOT NULL,
    name varchar(150) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id int(11) NOT NULL,
    permission_id int(11) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.auth_permission (
    id int(11) NOT NULL,
    name varchar(255) NOT NULL,
    content_type_id int(11) NOT NULL,
    codename varchar(100) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.django_admin_log (
    id int(11) NOT NULL,
    action_time timestamp NOT NULL,
    object_id text,
    object_repr varchar(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id int(11),
    user_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.django_content_type (
    id int(11) NOT NULL,
    app_label varchar(100) NOT NULL,
    model varchar(100) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied timestamp NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.django_session (
    session_key varchar(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.familyfees_family (
    id bigint NOT NULL,
    name varchar(100) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.familyfees_family_members (
    id bigint NOT NULL,
    family_id bigint NOT NULL,
    user_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.familyfees_familyfeerecord (
    id bigint NOT NULL,
    amount_to_pay numeric(10,2) NOT NULL,
    amount_paid numeric(10,2) NOT NULL,
    balance numeric(10,2) NOT NULL,
    academic_year_id bigint NOT NULL,
    family_id bigint NOT NULL,
    term_id bigint NOT NULL,
    date_created timestamp NOT NULL,
    is_fully_paid bool NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.familyfees_familypayment (
    id bigint NOT NULL,
    date date NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_method varchar(50),
    family_fee_record_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.fees_feestructure (
    id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    academic_year_id bigint NOT NULL,
    grade_class_id bigint NOT NULL,
    term_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.fees_payment (
    id bigint NOT NULL,
    date date NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_method varchar(50),
    student_fee_record_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.fees_studentfeerecord (
    id bigint NOT NULL,
    amount_paid numeric(10,2) NOT NULL,
    balance numeric(10,2) NOT NULL,
    is_fully_paid bool NOT NULL,
    fee_structure_id bigint NOT NULL,
    student_id bigint NOT NULL,
    date_created timestamp NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.principal_principalprofile (
    id bigint NOT NULL,
    user_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.staff_staffprofile (
    id bigint NOT NULL,
    user_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.student_academicyear (
    id bigint NOT NULL,
    name varchar(20) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.student_gradeclass (
    id bigint NOT NULL,
    name varchar(40) NOT NULL,
    staff_id bigint
) TYPE=MyISAM;

CREATE TABLE public.student_studentprofile (
    id bigint NOT NULL,
    last_school_attended varchar(255),
    class_seeking_admission_to varchar(20),
    is_immunized varchar(200),
    has_allergies varchar(10),
    allergic_foods text,
    has_peculiar_health_issues varchar(10),
    health_issues varchar(150),
    other_related_info text,
    name_of_father varchar(100),
    name_of_mother varchar(100),
    occupation_of_father varchar(100),
    occupation_of_mother varchar(100),
    nationality_of_father varchar(100),
    nationality_of_mother varchar(100),
    contact_of_father varchar(100),
    contact_of_mother varchar(100),
    house_number varchar(100),
    user_id bigint NOT NULL,
    current_class smallint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.student_studentsubjectrecord (
    id bigint NOT NULL,
    class_score double precision NOT NULL,
    exam_score double precision NOT NULL,
    total_score double precision,
    grade varchar(2),
    student_term_record_id bigint NOT NULL,
    subject_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.student_studenttermrecord (
    id bigint NOT NULL,
    attendance int(11) NOT NULL,
    comments text,
    grade_class_id bigint,
    student_id bigint NOT NULL,
    term_id bigint NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.student_subject (
    id bigint NOT NULL,
    name varchar(20) NOT NULL
) TYPE=MyISAM;

CREATE TABLE public.student_term (
    id bigint NOT NULL,
    name varchar(20) NOT NULL,
    academic_year_id bigint NOT NULL
) TYPE=MyISAM;

ALTER TABLE public.account_user_groups
    ADD CONSTRAINT account_user_groups_pkey PRIMARY KEY (id);
ALTER TABLE public.account_user
    ADD CONSTRAINT account_user_pkey PRIMARY KEY (id);
ALTER TABLE public.account_user_user_permissions
    ADD CONSTRAINT account_user_user_permissions_pkey PRIMARY KEY (id);
ALTER TABLE public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
ALTER TABLE public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
ALTER TABLE public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
ALTER TABLE public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
ALTER TABLE public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
ALTER TABLE public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
ALTER TABLE public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
ALTER TABLE public.familyfees_family_members
    ADD CONSTRAINT familyfees_family_members_pkey PRIMARY KEY (id);
ALTER TABLE public.familyfees_family
    ADD CONSTRAINT familyfees_family_pkey PRIMARY KEY (id);
ALTER TABLE public.familyfees_familyfeerecord
    ADD CONSTRAINT familyfees_familyfeerecord_pkey PRIMARY KEY (id);
ALTER TABLE public.familyfees_familypayment
    ADD CONSTRAINT familyfees_familypayment_pkey PRIMARY KEY (id);
ALTER TABLE public.fees_feestructure
    ADD CONSTRAINT fees_feestructure_pkey PRIMARY KEY (id);
ALTER TABLE public.fees_payment
    ADD CONSTRAINT fees_payment_pkey PRIMARY KEY (id);
ALTER TABLE public.fees_studentfeerecord
    ADD CONSTRAINT fees_studentfeerecord_pkey PRIMARY KEY (id);
ALTER TABLE public.principal_principalprofile
    ADD CONSTRAINT principal_principalprofile_pkey PRIMARY KEY (id);
ALTER TABLE public.staff_staffprofile
    ADD CONSTRAINT staff_staffprofile_pkey PRIMARY KEY (id);
ALTER TABLE public.student_academicyear
    ADD CONSTRAINT student_academicyear_pkey PRIMARY KEY (id);
ALTER TABLE public.student_gradeclass
    ADD CONSTRAINT student_gradeclass_pkey PRIMARY KEY (id);
ALTER TABLE public.student_studentprofile
    ADD CONSTRAINT student_studentprofile_pkey PRIMARY KEY (id);
ALTER TABLE public.student_studentsubjectrecord
    ADD CONSTRAINT student_studentsubjectrecord_pkey PRIMARY KEY (id);
ALTER TABLE public.student_studenttermrecord
    ADD CONSTRAINT student_studenttermrecord_pkey PRIMARY KEY (id);
ALTER TABLE public.student_subject
    ADD CONSTRAINT student_subject_pkey PRIMARY KEY (id);
ALTER TABLE public.student_term
    ADD CONSTRAINT student_term_pkey PRIMARY KEY (id);
