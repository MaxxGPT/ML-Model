pipeline {
			agent any
			environment {
    			BRANCH_DEPLOY = "${env.BRANCH_NAME}"
    			ENVAWSACCOUNTID = "${BRANCH_DEPLOY}-AWS_ACCOUNT_ID"
    			ENVAWSREGISTRYURL = "${BRANCH_DEPLOY}-AWS_REGISTRY_URL"
    			ENV_CLUSTER_NAME = "ml-${BRANCH_DEPLOY}"
    			ML_TASKDEF_NAME = "ml-${BRANCH_DEPLOY}"
    			DEV_COMMIT_MSG = "#manualrun"
			    ENV_DB_USERNAME = "${BRANCH_DEPLOY}-DB_USERNAME"
			    ENV_DB_PASSWORD = "${BRANCH_DEPLOY}-DB_PASSWORD"
			    ENV_DB_HOST = "${BRANCH_DEPLOY}-DB_HOST"
			    ENV_DB_PORT = "${BRANCH_DEPLOY}-DB_PORT"
			    ENV_DB_NAME = "${BRANCH_DEPLOY}-DB_NAME"
			    ENV_SOURCE_TABLE = "${BRANCH_DEPLOY}-SOURCE_TABLE"
			    ENV_NER_ENTITIES = "${BRANCH_DEPLOY}-NER_ENTITIES" 
			    ENV_LDA_FEATURES = "${BRANCH_DEPLOY}-LDA_FEATURES"
			    ENV_LDA_NO_TOP_WORDS = "${BRANCH_DEPLOY}-LDA_NO_TOP_WORDS"
    			}
		  	stages {
		        // stage('Check') {
		        // 		when {
			       //      	branch 'dev' 
			       //  	}
		        //     steps {

		        //         script {
		        //             commitMsg = sh(script: "git log -1 --pretty=%B", returnStdout: true).trim()
		        //             if (!(commitMsg.contains(DEV_COMMIT_MSG))) {
		        //                     env.SKIP_BUILD = 'yes'
		        //                     error('no manual run skipping!')
		        //             }
		        //         }
		        //     }
		        // }
		    	stage('build docker image') {
		    		when {
		            	anyOf { branch 'dev'; branch 'stage'; branch 'prod'; } 
		        	}
		      	steps {
		   	 		script {
		   	 			withCredentials([
            				string(credentialsId: ENVAWSACCOUNTID, variable: 'AWS_ACCOUNT_ID'),
            				string(credentialsId: ENVAWSREGISTRYURL, variable: 'AWS_REGISTRY_URL'),
            				string(credentialsId: 'AWS_DEFAULT_REGION', variable: 'AWS_DEFAULT_REGION')
            				])
          				 	{
   							sh '''
   								set +x
								localImageName="${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
								docker build -t ${localImageName} .
							'''
							}
		      			}
					}
				}
				stage('publish docker image'){
					when {
		            	anyOf { branch 'dev'; branch 'stage'; branch 'prod'; } 
		        	}
					steps {
						script {
						withCredentials([
            				string(credentialsId: ENVAWSACCOUNTID, variable: 'AWS_ACCOUNT_ID'),
            				string(credentialsId: ENVAWSREGISTRYURL, variable: 'AWS_REGISTRY_URL'),
            				string(credentialsId: 'AWS_DEFAULT_REGION', variable: 'AWS_DEFAULT_REGION')
            				])
	    					{
			        		sh '''        			
					            docker_login=\$(aws ecr get-login --registry-ids ${AWS_ACCOUNT_ID} --no-include-email --region ${AWS_DEFAULT_REGION})
								login_result=\$(\$docker_login)
								localImageName="${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
								latest_tag="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-latest"
								docker tag $localImageName \$latest_tag
								sha_tag="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
								docker tag $localImageName \$sha_tag
								docker push \$latest_tag
								docker push \$sha_tag
							'''
							}
						}
					}	
				}
				stage('ECS RUN DEV'){
					when {
		            	anyOf { branch 'dev'; } 
		        	}
					steps {
						script {
						withCredentials([
            				string(credentialsId: ENVAWSACCOUNTID, variable: 'AWS_ACCOUNT_ID'),
            				string(credentialsId: ENVAWSREGISTRYURL, variable: 'AWS_REGISTRY_URL'),
            				string(credentialsId: 'AWS_DEFAULT_REGION', variable: 'AWS_DEFAULT_REGION'),
            				string(credentialsId: 'AWS_ROLE_NAME', variable: 'AWS_ROLE_NAME'),
            				string(credentialsId: ENV_DB_PASSWORD, variable: 'ENV_DB_PASSWORD'),
            				string(credentialsId: ENV_DB_USERNAME, variable: 'ENV_DB_USERNAME'),
            				string(credentialsId: ENV_DB_HOST, variable: 'ENV_DB_HOST'),
            				string(credentialsId: ENV_DB_PORT, variable: 'ENV_DB_PORT'),
            				string(credentialsId: ENV_DB_NAME, variable: 'ENV_DB_NAME'),
            				string(credentialsId: ENV_SOURCE_TABLE, variable: 'ENV_SOURCE_TABLE'),
            				string(credentialsId: ENV_NER_ENTITIES, variable: 'ENV_NER_ENTITIES'),
            				string(credentialsId: ENV_LDA_FEATURES, variable: 'ENV_LDA_FEATURES'),
            				string(credentialsId: ENV_LDA_NO_TOP_WORDS, variable: 'ENV_LDA_NO_TOP_WORDS')
            				            				])
	    					{
			        		sh '''
			        			aws sts assume-role --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/${AWS_ROLE_NAME} --role-session-name Jenkins-deployment | grep -w 'AccessKeyId\\|SecretAccessKey\\|SessionToken' | awk '{print $2}' | sed 's/\"//g;s/\\,//'> awscre;
			        			export AWS_ACCESS_KEY_ID=`sed -n '1p' awscre`
			        			export AWS_SECRET_ACCESS_KEY=`sed -n '2p' awscre`
			        			export AWS_SECURITY_TOKEN=`sed -n '3p' awscre`
			        			aws sts get-caller-identity 
								sha_tag="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${AWS_REGISTRY_URL}:${BRANCH_DEPLOY}-${GIT_COMMIT}"
			    				sed -e "s;IMAGE_NAME;\$sha_tag;g" taskdef.json > taskdef_0.json
			    				sed -ie "s;AWS_DEFAULT_REGION;\$AWS_DEFAULT_REGION;g" taskdef_0.json
			    				sed -ie "s;ENV_DB_USERNAME;\$ENV_DB_USERNAME;g" taskdef_0.json
								sed -ie "s;ENV_DB_PASSWORD;\$ENV_DB_PASSWORD;g" taskdef_0.json
								sed -ie "s;ENV_DB_HOST;\$ENV_DB_HOST;g" taskdef_0.json
								sed -ie "s;ENV_DB_PORT;\$ENV_DB_PORT;g" taskdef_0.json
								sed -ie "s;ENV_DB_NAME;\$ENV_DB_NAME;g" taskdef_0.json
								sed -ie "s;ENV_SOURCE_TABLE;\$ENV_SOURCE_TABLE;g" taskdef_0.json
								sed -ie "s;ENV_NER_ENTITIES;\$ENV_NER_ENTITIES;g" taskdef_0.json
								sed -ie "s;ENV_LDA_FEATURES;\$ENV_LDA_FEATURES;g" taskdef_0.json
								sed -ie "s;ENV_LDA_NO_TOP_WORDS;\$ENV_LDA_NO_TOP_WORDS;g" taskdef_0.json
			    				
			    				sed -ie "s;ML_TASKDEF_NAME;\$ML_TASKDEF_NAME;g" taskdef_0.json
			    				
			    				export TASK_VERSION=$(aws ecs register-task-definition --cli-input-json file://taskdef_0.json | jq --raw-output '.taskDefinition.revision')
			    				if [ -n "$TASK_VERSION" ]; then
			    				echo "Registered ECS Task Definition: " $TASK_VERSION
			    				else
    								echo "exit: No task definition"
    								exit;
								fi

								QUEUE_URL="https://sqs.${AWS_DEFAULT_REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/ml-startecsinstances"
								aws sqs send-message --queue-url ${QUEUE_URL} --message-body "jenkins ml dev manualrun trigger" --region ${AWS_DEFAULT_REGION}
								ContainerInstancesCount=$(aws ecs describe-clusters --region ${AWS_DEFAULT_REGION} --cluster $ENV_CLUSTER_NAME | jq .clusters[].registeredContainerInstancesCount)
								while [ $ContainerInstancesCount != 1 ]; do
									echo " checking container instance count"
									ContainerInstancesCount=$(aws ecs describe-clusters --region ${AWS_DEFAULT_REGION} --cluster $ENV_CLUSTER_NAME | jq .clusters[].registeredContainerInstancesCount)
								done
								aws ecs run-task --cluster $ENV_CLUSTER_NAME --task-definition $ML_TASKDEF_NAME:$TASK_VERSION --count 1 --region=${AWS_DEFAULT_REGION}
								echo "Task started check cloudwatch!!!"

							'''	
							}
						}
					}	
				}


			}
		}
