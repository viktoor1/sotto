# PR created: #703

[Open the actual pull request](https://github.com/getsotto/sotto/pull/703). The contributor completed the steps below. CI currently awaits maintainer approval.

The following instructions are retained as the historical browser submission path.

# Open the prepared Sotto #637 pull request

The repair and its documentation are already pushed to your fork. The GitHub API
returned Forbidden, so no pull request has been created by the assistant.

1. [Open the prefilled pull-request page](https://github.com/getsotto/sotto/compare/main...viktoor1:fix/637-administrator-retry?expand=1&title=fix%28web%29%3A+retry+administrator+loading+for+payer+transfers&body=When+administrator+loading+fails+in+Change+who+pays%2C+the+organisation+stays+selected%0Abut+there+is+no+way+to+reload+its+administrators.+Add+a+labelled+retry+for+that%0Aorganisation%2C+with+separate+discovery+error%2Floading+state+and+an+immediate+request%0Alock.+Retry+clears+the+old+discovery+error+and+calls+neither+the+quote+nor+transfer+API.%0A%0AAdd+nine+regression+cases+covering+recovery%2C+pending%2Fduplicate+requests%2C+repeated%0Afailure%2C+empty+results%2C+selection+reset+and+quote%2Fsubmission+error+isolation.+Preserve%0Athe+upstream+organisation-list+recovery+flow+and+sponsored+transfers.%0A%0AValidation%3A%0A%0A-+Payer-transfer+component+suite%3A+%2A%2A28+passed%2A%2A.%0A-+TypeScript+checks+and+production+Vite+build+passed.%0A-+Full+configured+web+component+suite%3A+%2A%2A272+passed%2C+1+failed%2A%2A.+The+existing+1+MiB%0A++Base64+test+exceeded+its+15-second+limit%3B+the+same+timeout+reproduced+in+isolation%0A++on+clean+upstream+%60de5a0e4%60%2C+with+this+repair+removed.+Its+timeout+and+assertions%0A++are+unchanged.%0A%0AInvestigation+documentation+is+available+separately+from+the+focused+code+diff%3A%0A%0A-+%5BDiscovery+path+and+repair+review%5D%28https%3A%2F%2Fgithub.com%2Fviktoor1%2Fsotto%2Fblob%2Fevidence%2F637-investigation%2Frepair-review.md%29%0A-+%5BInteractive+HTML+walkthrough%5D%28https%3A%2F%2Fgithub.com%2Fviktoor1%2Fsotto%2Fblob%2Fevidence%2F637-investigation%2Finteractive-walkthrough.html%29+-+download+and+open+locally%3B+this+preserves+the+original+investigation+snapshot+and+proposed-code+labels.%0A-+%5BTask+journal+and+recorded+activity%5D%28https%3A%2F%2Fgithub.com%2Fviktoor1%2Fsotto%2Fblob%2Fevidence%2F637-investigation%2Ftask-journal.md%29%0A-+%5BDownload+the+complete+evidence+branch%5D%28https%3A%2F%2Fgithub.com%2Fviktoor1%2Fsotto%2Farchive%2Frefs%2Fheads%2Fevidence%2F637-investigation.zip%29%0A%0AThe+records+retain+the+original+missing-retry+failure%2C+the+successful+recovery%0Atests%2C+a+negative+control+demonstrating+the+duplicate-request+check%2C+and+the%0Aunchanged-upstream+timeout+evidence.%0A%0AFixes+%23637.%0A). Sign in as `viktoor1` if asked.
2. Confirm **base: getsotto/sotto, main** and **head: viktoor1/sotto, fix/637-administrator-retry**.
3. Review the prefilled title/body and click **Create pull request**.

The description includes the existing Base64 timeout and links to the HTML,
discovery/repair review, journal and full evidence download. If GitHub does not
retain the body from the URL, copy it from [pr-body.md](pr-body.md).

Then share the new PR URL in the original chat so it can be attached and its CI
checks inspected. The contributor will write their own issue follow-up comment.

- [Code commit](https://github.com/viktoor1/sotto/commit/e879c71f0e5a5d1b9e3d1219a89f80e7c5c040b8)
- [Evidence branch](https://github.com/viktoor1/sotto/tree/evidence/637-investigation)
- [Interactive HTML](interactive-walkthrough.html)
- [Discovery path](discovery-path.md)
- [Task journal](task-journal.md)
