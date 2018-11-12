# gimel_py
python library for running particle accelerator simulator 'gimel' Tel-Aviv University

# Before using

Before using this code, one must create a file named `auth.json` in the directory of the code. this file must have the following format:

```json

  {
  "username":"<your TAU username>",
  "password":"<your TAU password>",
  "id":"<your ID number>"

}
```

the username and password must be the same as those needed to access an account on `gp.tau.ac.il` via `ssh` (i.e. you need to have a general physics account in Tel Aviv University)

