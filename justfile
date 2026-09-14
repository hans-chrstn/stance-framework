set shell := ["bash", "-euo", "pipefail", "-c"]

root := justfile_directory()

default: verify

doctor:
    @bash "{{root}}/scripts/doctor.sh"

contract-check:
    @bash "{{root}}/scripts/contract-check.sh"

gate0: doctor contract-check

fmt-check:
    @bash "{{root}}/scripts/not-implemented.sh" fmt-check

lint:
    @bash "{{root}}/scripts/not-implemented.sh" lint

validate:
    @bash "{{root}}/scripts/not-implemented.sh" validate

plan:
    @bash "{{root}}/scripts/not-implemented.sh" plan

test-unit:
    @bash "{{root}}/scripts/not-implemented.sh" test-unit

test:
    @bash "{{root}}/scripts/not-implemented.sh" test

build:
    @bash "{{root}}/scripts/not-implemented.sh" build

generate-oar:
    @bash "{{root}}/scripts/not-implemented.sh" generate-oar

package:
    @bash "{{root}}/scripts/not-implemented.sh" package

deploy-test:
    @bash "{{root}}/scripts/not-implemented.sh" deploy-test

game-test suite:
    @bash "{{root}}/scripts/not-implemented.sh" "game-test {{suite}}"

verify:
    @bash "{{root}}/scripts/not-implemented.sh" verify
