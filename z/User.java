package com.packt.football.account.models;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;


@Entity
@Table(name = "users")
@Data               // Generates getters, setters, toString, equals, hashCode
@NoArgsConstructor  // Generates a no-arg constructor
@AllArgsConstructor // Generates an all-args constructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = true)
    private String userId;

    private String fullName;
    private String password;

    @Enumerated(EnumType.STRING)
    private Role role;
    private Gender gender;
    private String nationality;

    private boolean isActive = true;
    private boolean isStaff = false;

    @column(name ="date_of_birth", nullable=true)
    private LocalDate dateOfBirth;

    public enum Role{
        STUDENT,
        STAFF,
        PRINCIPAL
    }

    public enum Gender{
        MALE,
        FEMALE
    }





}