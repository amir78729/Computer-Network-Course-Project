SQLite format 3   @                                                                     .4 � 	� ��Ie	�                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    �''�wtableusers_commitsusers_commitsCREATE TABLE users_commits (
                                                                        username text,
                                                                        repository text,
                                                                        file_path text,
                                                                        file_content text,
                                                                        message text, 
                                                                        commit_time text
                                                                    )�11�]tableusers_repositoriesusers_repositoriesCREATE TABLE users_repositories (
                                                        username text,
                                                        repo_name text,
                                                        prvt_or_pblc text,
                                                        contributor text, 
                                                        CONSTRAINT PK_user PRIMARY KEY (username,repo_name)
                                                    )CW1 indexsqlite_autoindex_users_repositories_1users_repositories�++�Otableusers_passwordsusers_passwordsCREATE TABLE users_passwords (
                                                    username text PRIMARY KEY,
                                                    password text
                                                )=Q+ indexsqlite_autoindex_users_passwords_1users_passwords          � ���                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             332211
   � ���                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 32	1� � ������                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 111PRVT1 3332PBLC3222PBLC2112PBLC1331PRVT3221PRVT2   111PRVT1
   � ������                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       332222112331221	111   � ��h�;��G�                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   T[A221New Text Document - Copy (4) - Copy.txtasdsadsa22021-05-19 02:55:41.608492M
MA221New Text Document - Copy (3).txtasdsadsa22021-05-19 02:55:41.608492T	[A221New Text Document - Copy (3) - Copy.txtasdsadsa22021-05-19 02:55:41.608492MMA221New Text Document - Copy (2).txtasdsadsa22021-05-19 02:55:41.608492B7A221New Text Document.txtasdsadsa12021-05-19 02:55:26.893862IEA221New Text Document - Copy.txtasdsadsa12021-05-19 02:55:26.893862MMA221New Text Document - Copy (3).txtasdsadsa12021-05-19 02:55:26.893862MMA221New Text Document - Copy (2).txtasdsadsa12021-05-19 02:55:26.893862/A112time.txt1232021-05-19 01:42:33.1940156+A112time - Copy.txt1232021-05-19 01:42:33.194015-A112time.txt12021-05-19 01:21:45.149410