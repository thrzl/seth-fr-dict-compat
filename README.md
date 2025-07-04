# seth-fr-dict-compat
french yomitan dictionary that removes certain oddities with [seth's french dictionary](https://github.com/seth-js/yomichan-fr)

being completely real. do not look at the code. it's that bad. 

i might clean it up another time but for now just download the dictionary from the release

## summary of changes
seth's dictionary had this random thing where it would have "non-lemma" entries for non-base form (non-lemma) entries with weirdly formatted data. this dictionary changes them to instead point to the base form, like this:

<img width="376" alt="image" src="https://github.com/user-attachments/assets/48ac13ac-a8d9-465b-8eb9-2822b2d29f27" />

<details>
<summary>example of non-lemma entry:</summary>
<br>
  
![](https://github.com/user-attachments/assets/2cb3560f-b788-4f20-af92-710eaa5f90f2)

from what i gather it's SUPPOSED to look like this when you use his custom yomitan version, but i didnt want to use it cus it hasnt been updated in like 2 years

![screenshot of intended formatting](https://user-images.githubusercontent.com/83692925/216894602-efd6c118-f46d-4062-8864-4a75ba5d6751.png)
</details>

there definitely may be some issues. PLEASE report them because i'll probably run into them later and i'd like to fix it before then

i recommend keeping kty-fr-en or the REAL seth's dictionary around just in case
